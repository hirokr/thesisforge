from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.citation import CitationAgent
from app.db.base import Base
from app.models import Agent, AgentFinding, AnalysisRun, CitationCheck, Document, DocumentChunk, Reference, ThesisProject, UserProfile
from app.services.llm_service import LLMRequest, LLMResponse


class FakeLLMService:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text=self.response_text, provider="openai", model="gpt-test", usage={})


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db
    Base.metadata.drop_all(engine)


def seed_citation_records(db: Session) -> dict[str, object]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Agentic Thesis")
    document = Document(project=project, filename="draft.txt", document_type="thesis_draft")
    chunk = DocumentChunk(document=document, chunk_index=0, content="Multi-agent review improves thesis quality.")
    reference = Reference(
        project=project,
        document=document,
        citation_key="smith2024",
        title="Multi-agent thesis review",
        authors=["Smith"],
        year=2024,
    )
    analysis_run = AnalysisRun(project=project)
    agent = Agent(
        name="Citation Agent",
        slug="citation",
        description="Checks citations.",
        system_prompt="Check citations.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, document, chunk, reference, analysis_run, agent])
    db.commit()
    return {
        "chunk": chunk,
        "reference": reference,
        "analysis_run": analysis_run,
        "agent": agent,
    }


def test_citation_agent_outputs_expected_sections() -> None:
    response_text = """{
        "unsupported_or_weak_claims": ["Chunk 0 overstates review quality improvements."],
        "citation_checks": [
            {
                "claim_text": "Multi-agent review improves thesis quality.",
                "status": "weakly_supported",
                "confidence": 0.45,
                "notes": "Provided reference is related but does not prove quality gains.",
                "citation_key": "smith2024"
            }
        ],
        "handoff_summary": "One claim needs stronger citation support.",
        "findings": [
            {
                "category": "citation",
                "severity": "high",
                "title": "Quality-improvement claim is weakly supported",
                "description": "The draft makes a causal improvement claim without matching evidence.",
                "evidence": {"chunk_index": 0, "citation_key": "smith2024"},
                "recommendation": "Add an evaluation citation or narrow the claim."
            }
        ]
    }"""
    llm_service = FakeLLMService(response_text)
    agent = CitationAgent(llm_service=llm_service)

    result = agent.run_review(
        document_chunks=[{"id": "chunk-1", "chunk_index": 0, "content": "Multi-agent review improves thesis quality."}],
        references=[{"citation_key": "smith2024", "title": "Multi-agent thesis review"}],
        literature_findings=[{"title": "Unsupported prior-work claim"}],
    )

    assert result.raw_output["citation_checks"][0]["status"] == "weakly_supported"
    assert result.findings[0].title == "Quality-improvement claim is weakly supported"
    assert agent.handoff_summary(result) == "One claim needs stronger citation support."
    assert "Do not claim external verification" in llm_service.requests[0].user_prompt


def test_citation_agent_handles_missing_references_in_prompt() -> None:
    llm_service = FakeLLMService('{"citation_checks": [], "findings": []}')
    agent = CitationAgent(llm_service=llm_service)

    result = agent.run_review(
        document_chunks=[{"id": "chunk-1", "chunk_index": 0, "content": "Draft claim"}],
        references=[],
        literature_findings=[],
    )

    assert result.raw_output["unsupported_or_weak_claims"] == []
    assert result.raw_output["handoff_summary"].startswith("Citation review checks:")
    assert "No references were provided" in llm_service.requests[0].user_prompt


def test_citation_agent_saves_findings_and_citation_checks(db: Session) -> None:
    records = seed_citation_records(db)
    reference_id: UUID = records["reference"].id
    analysis_run_id: UUID = records["analysis_run"].id
    agent_id: UUID = records["agent"].id
    response_text = f"""{{
        "citation_checks": [
            {{
                "claim_text": "Multi-agent review improves thesis quality.",
                "status": "unsupported",
                "confidence": 0.3,
                "notes": "The provided source is not enough for this claim.",
                "reference_id": "{reference_id}"
            }}
        ],
        "findings": [
            {{
                "category": "citation",
                "severity": "high",
                "title": "Unsupported improvement claim",
                "description": "The cited evidence does not support the claim.",
                "evidence": {{"reference_id": "{reference_id}"}},
                "recommendation": "Add stronger evidence."
            }}
        ]
    }}"""
    agent = CitationAgent(llm_service=FakeLLMService(response_text))

    result = agent.run_and_save(
        db,
        analysis_run_id=analysis_run_id,
        agent_id=agent_id,
        document_chunks=[records["chunk"]],
        references=[records["reference"]],
        literature_findings=[],
    )

    findings = db.scalars(select(AgentFinding)).all()
    citation_checks = db.scalars(select(CitationCheck)).all()

    assert len(result.findings) == 1
    assert len(findings) == 1
    assert findings[0].analysis_run_id == analysis_run_id
    assert findings[0].agent_id == agent_id
    assert findings[0].title == "Unsupported improvement claim"
    assert len(citation_checks) == 1
    assert citation_checks[0].analysis_run_id == analysis_run_id
    assert citation_checks[0].reference_id == reference_id
    assert citation_checks[0].claim_text == "Multi-agent review improves thesis quality."
    assert citation_checks[0].status == "unsupported"
