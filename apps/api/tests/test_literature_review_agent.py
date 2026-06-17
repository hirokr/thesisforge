from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.literature_review import LiteratureReviewAgent
from app.db.base import Base
from app.models import Agent, AgentFinding, AnalysisRun, Document, DocumentChunk, Reference, ThesisProject, UserProfile
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


def seed_review_records(db: Session) -> dict[str, object]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Agentic Thesis", research_gap="Weak support gap")
    document = Document(project=project, filename="draft.txt", document_type="thesis_draft")
    chunk = DocumentChunk(document=document, chunk_index=0, content="Prior work is limited, but no citations are provided.")
    reference = Reference(
        project=project,
        document=document,
        citation_key="smith2024",
        title="Multi-agent thesis review",
        authors=["Smith"],
        year=2024,
        venue="AI Education",
    )
    analysis_run = AnalysisRun(project=project)
    agent = Agent(
        name="Literature Review Agent",
        slug="literature-review",
        description="Reviews literature.",
        system_prompt="Review literature.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, document, chunk, reference, analysis_run, agent])
    db.commit()
    return {
        "project": project,
        "chunk": chunk,
        "reference": reference,
        "analysis_run": analysis_run,
        "agent": agent,
    }


def test_literature_review_agent_outputs_expected_sections() -> None:
    response_text = """{
        "major_literature_themes": ["agent review workflows"],
        "claim_support_observations": ["The draft mentions prior work but gives little detail."],
        "weak_or_missing_citation_warnings": ["Chunk 0 needs a citation for limited prior work."],
        "suggested_literature_gaps": ["Clarify how workflow orchestration differs from prior tools."],
        "handoff_summary": "Gap should be narrowed before the research-gap review.",
        "findings": [
            {
                "category": "literature_review",
                "severity": "high",
                "title": "Unsupported prior-work claim",
                "description": "The claim about limited prior work is not tied to a reference.",
                "evidence": {"chunk_index": 0},
                "recommendation": "Attach the claim to a recent source or soften it."
            }
        ]
    }"""
    llm_service = FakeLLMService(response_text)
    agent = LiteratureReviewAgent(llm_service=llm_service, model="gpt-test")

    result = agent.run_review(
        project_context={"title": "Agentic Thesis", "research_gap": "Weak support gap"},
        references=[{"citation_key": "smith2024", "title": "Multi-agent thesis review"}],
        document_chunks=[{"id": "chunk-1", "chunk_index": 0, "content": "Prior work is limited."}],
    )

    assert result.raw_output["major_literature_themes"] == ["agent review workflows"]
    assert result.raw_output["weak_or_missing_citation_warnings"] == ["Chunk 0 needs a citation for limited prior work."]
    assert result.findings[0].title == "Unsupported prior-work claim"
    assert agent.handoff_summary(result) == "Gap should be narrowed before the research-gap review."
    assert "Do not claim web or external database verification" in llm_service.requests[0].user_prompt


def test_literature_review_agent_handles_missing_references_in_prompt() -> None:
    llm_service = FakeLLMService('{"major_literature_themes": [], "findings": []}')
    agent = LiteratureReviewAgent(llm_service=llm_service)

    result = agent.run_review(
        project_context={"title": "Agentic Thesis"},
        references=[],
        document_chunks=[{"id": "chunk-1", "chunk_index": 0, "content": "Draft text"}],
    )

    assert result.raw_output["suggested_literature_gaps"] == []
    assert result.raw_output["handoff_summary"].startswith("Literature review themes:")
    assert "No references were provided" in llm_service.requests[0].user_prompt


def test_literature_review_agent_saves_findings(db: Session) -> None:
    response_text = """{
        "findings": [
            {
                "category": "literature_review",
                "severity": "medium",
                "title": "Missing synthesis",
                "description": "References are listed but not synthesized.",
                "evidence": {"reference_count": 1},
                "recommendation": "Group references by theme."
            }
        ],
        "handoff_summary": "Literature synthesis needs work."
    }"""
    records = seed_review_records(db)
    analysis_run_id: UUID = records["analysis_run"].id
    agent_id: UUID = records["agent"].id
    agent = LiteratureReviewAgent(llm_service=FakeLLMService(response_text))

    result = agent.run_and_save(
        db,
        analysis_run_id=analysis_run_id,
        agent_id=agent_id,
        project_context={"title": records["project"].title},
        references=[records["reference"]],
        document_chunks=[records["chunk"]],
    )

    findings = db.scalars(select(AgentFinding)).all()

    assert len(result.findings) == 1
    assert len(findings) == 1
    assert findings[0].analysis_run_id == analysis_run_id
    assert findings[0].agent_id == agent_id
    assert findings[0].title == "Missing synthesis"
    assert findings[0].evidence == {"reference_count": 1}
