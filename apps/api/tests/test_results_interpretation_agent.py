from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.results_interpretation import ResultsInterpretationAgent
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
        objectives="Evaluate review quality against a baseline.",
        methodology_summary="Compare multi-agent review with a single-agent baseline.",
        results_summary="Multi-agent review was better.",
    )
    analysis_run = AnalysisRun(project=project)
    agent = Agent(
        name="Results Interpretation Agent",
        slug="results-interpretation",
        description="Reviews result interpretation.",
        system_prompt="Review results.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, analysis_run, agent])
    db.commit()
    return {"project": project, "analysis_run": analysis_run, "agent": agent}


def test_results_interpretation_agent_outputs_expected_sections() -> None:
    response_text = """{
        "results_interpretation_score": 64,
        "overclaiming_warnings": ["The summary claims the workflow is better without reporting effect size."],
        "missing_comparison_warnings": ["No confidence intervals or statistical comparison are discussed."],
        "suggested_discussion_points": ["Discuss baseline variance and reviewer agreement."],
        "handoff_summary": "Results need stronger comparison language before report generation.",
        "findings": [
            {
                "category": "results_interpretation",
                "severity": "high",
                "title": "Improvement claim lacks quantified support",
                "description": "The result summary states improvement without enough comparative evidence.",
                "evidence": {"field": "results_summary"},
                "recommendation": "Report metrics, baseline deltas, and uncertainty."
            }
        ]
    }"""
    llm_service = FakeLLMService(response_text)
    agent = ResultsInterpretationAgent(llm_service=llm_service)

    result = agent.run_review(
        results_summary="Multi-agent review was better.",
        methodology_summary="Compare multi-agent review with a single-agent baseline.",
        objectives="Evaluate review quality against a baseline.",
        csv_metadata={"row_count": 10, "column_names": ["method", "score"]},
        previous_agent_findings=[{"title": "Missing baseline comparison"}],
    )

    assert result.raw_output["results_interpretation_score"] == 64
    assert result.raw_output["suggested_discussion_points"][0] == "Discuss baseline variance and reviewer agreement."
    assert result.findings[0].title == "Improvement claim lacks quantified support"
    assert agent.handoff_summary(result) == "Results need stronger comparison language before report generation."
    assert '"has_csv_metadata": true' in llm_service.requests[0].user_prompt


def test_results_interpretation_agent_handles_missing_results_summary() -> None:
    llm_service = FakeLLMService('{"overclaiming_warnings": [], "findings": []}')
    agent = ResultsInterpretationAgent(llm_service=llm_service)

    result = agent.run_review(
        results_summary="",
        methodology_summary="Compare methods.",
        objectives="Evaluate quality.",
    )

    assert result.raw_output["results_interpretation_score"] is None
    assert result.raw_output["missing_comparison_warnings"] == []
    assert '"missing_results_summary": true' in llm_service.requests[0].user_prompt


def test_results_interpretation_agent_saves_findings(db: Session) -> None:
    response_text = """{
        "findings": [
            {
                "category": "results_interpretation",
                "severity": "medium",
                "title": "Missing discussion of limitations",
                "description": "The result summary does not discuss when the method fails.",
                "evidence": {"field": "results_summary"},
                "recommendation": "Add limitations and failure-case analysis."
            }
        ],
        "handoff_summary": "Limitations discussion is missing."
    }"""
    records = seed_run_records(db)
    analysis_run_id: UUID = records["analysis_run"].id
    agent_id: UUID = records["agent"].id
    project: ThesisProject = records["project"]
    agent = ResultsInterpretationAgent(llm_service=FakeLLMService(response_text))

    result = agent.run_and_save(
        db,
        analysis_run_id=analysis_run_id,
        agent_id=agent_id,
        results_summary=project.results_summary,
        methodology_summary=project.methodology_summary,
        objectives=project.objectives,
        csv_metadata={"row_count": 10},
    )

    findings = db.scalars(select(AgentFinding)).all()

    assert len(result.findings) == 1
    assert len(findings) == 1
    assert findings[0].analysis_run_id == analysis_run_id
    assert findings[0].agent_id == agent_id
    assert findings[0].title == "Missing discussion of limitations"
    assert findings[0].evidence == {"field": "results_summary"}
