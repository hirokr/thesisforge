from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.methodology_consistency import MethodologyConsistencyAgent
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
    project = ThesisProject(
        owner=owner,
        title="Agentic Thesis",
        research_gap="Multi-agent thesis review lacks workflow evaluation.",
        objectives="Evaluate review quality and usability.",
    )
    analysis_run = AnalysisRun(project=project)
    agent = Agent(
        name="Methodology Consistency Agent",
        slug="methodology-consistency",
        description="Checks methodology consistency.",
        system_prompt="Check methodology.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, analysis_run, agent])
    db.commit()
    return {"project": project, "analysis_run": analysis_run, "agent": agent}


def test_methodology_consistency_agent_outputs_expected_sections() -> None:
    response_text = """{
        "methodology_consistency_score": 58,
        "mismatch_warnings": ["Objective promises usability evaluation, but methodology only describes model prompting."],
        "missing_baselines_or_ablations": ["No baseline against single-agent review.", "No ablation for citation agent."],
        "suggested_fixes": ["Add a baseline comparison and define review-quality metrics."],
        "handoff_summary": "Methodology needs baseline and metric details before results interpretation.",
        "findings": [
            {
                "category": "methodology",
                "severity": "high",
                "title": "Missing baseline comparison",
                "description": "The methodology does not include a baseline for the multi-agent workflow.",
                "evidence": {"field": "methodology_summary"},
                "recommendation": "Compare against a single-agent or manual review baseline."
            }
        ]
    }"""
    llm_service = FakeLLMService(response_text)
    agent = MethodologyConsistencyAgent(llm_service=llm_service)

    result = agent.run_review(
        research_gap="Multi-agent thesis review lacks workflow evaluation.",
        objectives="Evaluate review quality and usability.",
        methodology_summary="We prompt multiple agents and summarize feedback.",
        dataset_summary="Ten thesis drafts.",
        results_summary="The workflow improved feedback.",
        previous_agent_findings=[{"title": "Unsupported improvement claim"}],
    )

    assert result.raw_output["methodology_consistency_score"] == 58
    assert result.raw_output["missing_baselines_or_ablations"][0] == "No baseline against single-agent review."
    assert result.findings[0].title == "Missing baseline comparison"
    assert agent.handoff_summary(result) == "Methodology needs baseline and metric details before results interpretation."
    assert "do not invent experimental evidence" in llm_service.requests[0].user_prompt


def test_methodology_consistency_agent_handles_missing_methodology_in_prompt() -> None:
    llm_service = FakeLLMService('{"mismatch_warnings": ["No methodology provided"], "findings": []}')
    agent = MethodologyConsistencyAgent(llm_service=llm_service)

    result = agent.run_review(
        research_gap="Gap",
        objectives="Objectives",
        methodology_summary="",
        dataset_summary=None,
        results_summary=None,
        previous_agent_findings=[],
    )

    assert result.raw_output["methodology_consistency_score"] is None
    assert result.raw_output["suggested_fixes"] == []
    assert '"missing_methodology_summary": true' in llm_service.requests[0].user_prompt
    assert '"missing_dataset_summary": true' in llm_service.requests[0].user_prompt


def test_methodology_consistency_agent_saves_findings(db: Session) -> None:
    response_text = """{
        "findings": [
            {
                "category": "methodology",
                "severity": "medium",
                "title": "Dataset detail missing",
                "description": "The dataset summary does not describe sample size or source.",
                "evidence": {"field": "dataset_summary"},
                "recommendation": "Add dataset source, sample size, and inclusion criteria."
            }
        ],
        "handoff_summary": "Dataset detail is incomplete."
    }"""
    records = seed_run_records(db)
    analysis_run_id: UUID = records["analysis_run"].id
    agent_id: UUID = records["agent"].id
    project: ThesisProject = records["project"]
    agent = MethodologyConsistencyAgent(llm_service=FakeLLMService(response_text))

    result = agent.run_and_save(
        db,
        analysis_run_id=analysis_run_id,
        agent_id=agent_id,
        research_gap=project.research_gap,
        objectives=project.objectives,
        methodology_summary="Prompt multiple agents.",
        dataset_summary="Thesis drafts.",
        results_summary="Improved feedback.",
        previous_agent_findings=[],
    )

    findings = db.scalars(select(AgentFinding)).all()

    assert len(result.findings) == 1
    assert len(findings) == 1
    assert findings[0].analysis_run_id == analysis_run_id
    assert findings[0].agent_id == agent_id
    assert findings[0].title == "Dataset detail missing"
    assert findings[0].evidence == {"field": "dataset_summary"}
