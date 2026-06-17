from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.research_gap import ResearchGapAgent
from app.db.base import Base
from app.models import Agent, AgentFinding, AnalysisRun, ThesisProject, UserProfile
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


def seed_run_records(db: Session) -> dict[str, object]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Agentic Thesis", research_gap="Broad gap")
    analysis_run = AnalysisRun(project=project)
    agent = Agent(
        name="Research Gap Agent",
        slug="research-gap",
        description="Reviews research gaps.",
        system_prompt="Review gaps.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, analysis_run, agent])
    db.commit()
    return {"project": project, "analysis_run": analysis_run, "agent": agent}


def test_research_gap_agent_outputs_expected_sections() -> None:
    response_text = """{
        "gap_quality_score": 62,
        "weaknesses": ["The gap is broad.", "The novelty claim is unsupported."],
        "improved_research_gap_suggestion": "Narrow the gap to orchestration failures in thesis-review agents.",
        "missing_evidence": ["Recent comparison with existing writing assistants"],
        "handoff_summary": "Methodology should address the narrowed orchestration gap.",
        "findings": [
            {
                "category": "research_gap",
                "severity": "high",
                "title": "Gap is too broad",
                "description": "The stated gap does not identify a specific unresolved problem.",
                "evidence": {"field": "research_gap"},
                "recommendation": "Define who is affected, what is missing, and why current tools fail."
            }
        ]
    }"""
    llm_service = FakeLLMService(response_text)
    agent = ResearchGapAgent(llm_service=llm_service)

    result = agent.run_review(
        problem_statement="Thesis students struggle to interpret review feedback.",
        research_gap="There is limited AI support.",
        objectives="Build and evaluate a multi-agent workflow.",
        literature_findings=[{"title": "Unsupported prior-work claim", "severity": "high"}],
    )

    assert result.raw_output["gap_quality_score"] == 62
    assert result.raw_output["improved_research_gap_suggestion"].startswith("Narrow the gap")
    assert result.findings[0].title == "Gap is too broad"
    assert agent.handoff_summary(result) == "Methodology should address the narrowed orchestration gap."
    assert "Use the provided literature findings only" in llm_service.requests[0].user_prompt


def test_research_gap_agent_handles_empty_gap_in_prompt() -> None:
    llm_service = FakeLLMService('{"weaknesses": ["No gap provided"], "findings": []}')
    agent = ResearchGapAgent(llm_service=llm_service)

    result = agent.run_review(
        problem_statement="Students need structured review.",
        research_gap="",
        objectives="Create an assistant.",
        literature_findings=[],
    )

    assert result.raw_output["gap_quality_score"] is None
    assert result.raw_output["missing_evidence"] == []
    assert '"empty_research_gap": true' in llm_service.requests[0].user_prompt


def test_research_gap_agent_saves_findings(db: Session) -> None:
    response_text = """{
        "findings": [
            {
                "category": "research_gap",
                "severity": "medium",
                "title": "Missing evidence",
                "description": "The gap needs literature support.",
                "evidence": {"literature_finding_ids": ["finding-1"]},
                "recommendation": "Cite a concrete unmet limitation."
            }
        ],
        "handoff_summary": "Gap evidence is incomplete."
    }"""
    records = seed_run_records(db)
    analysis_run_id: UUID = records["analysis_run"].id
    agent_id: UUID = records["agent"].id
    agent = ResearchGapAgent(llm_service=FakeLLMService(response_text))

    result = agent.run_and_save(
        db,
        analysis_run_id=analysis_run_id,
        agent_id=agent_id,
        problem_statement="Students need structured review.",
        research_gap="AI support is limited.",
        objectives="Create an assistant.",
        literature_findings=[{"id": "finding-1", "title": "Unsupported claim"}],
    )

    findings = db.scalars(select(AgentFinding)).all()

    assert len(result.findings) == 1
    assert len(findings) == 1
    assert findings[0].analysis_run_id == analysis_run_id
    assert findings[0].agent_id == agent_id
    assert findings[0].title == "Missing evidence"
    assert findings[0].evidence == {"literature_finding_ids": ["finding-1"]}
