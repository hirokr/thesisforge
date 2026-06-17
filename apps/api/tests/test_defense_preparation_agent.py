from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.defense_preparation import DefensePreparationAgent
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
        title="Agentic Thesis Review",
        research_gap="Multi-agent thesis review lacks defense-readiness evaluation.",
    )
    analysis_run = AnalysisRun(project=project)
    agent = Agent(
        name="Defense Preparation Agent",
        slug="defense-preparation",
        description="Generates likely thesis defense questions.",
        system_prompt="Prepare defense questions.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, analysis_run, agent])
    db.commit()
    return {"project": project, "analysis_run": analysis_run, "agent": agent}


def test_defense_preparation_agent_outputs_questions() -> None:
    response_text = """{
        "defense_questions": [
            {
                "question": "Why is a multi-agent workflow necessary instead of a single reviewer model?",
                "category": "methodology",
                "risk_level": "high",
                "suggested_answer_points": ["Connect the design to role-specialized review.", "Discuss baseline comparison plans."]
            },
            {
                "question": "How did you validate citation-support warnings?",
                "category": "citation",
                "risk_level": "medium",
                "suggested_answer_points": ["Explain the limits of provided-reference checks."]
            }
        ],
        "handoff_summary": "Two defense questions need priority preparation.",
        "findings": [
            {
                "category": "defense",
                "severity": "high",
                "title": "Defense needs baseline justification",
                "description": "Prior findings show the thesis may be challenged on baseline comparisons.",
                "evidence": {"source_finding": "Missing baseline comparison"},
                "recommendation": "Prepare a concise baseline rationale and experiment plan."
            }
        ]
    }"""
    llm_service = FakeLLMService(response_text)
    agent = DefensePreparationAgent(llm_service=llm_service)

    result = agent.run_review(
        previous_agent_findings=[
            {
                "category": "methodology",
                "severity": "high",
                "title": "Missing baseline comparison",
            }
        ],
        project_context={"title": "Agentic Thesis Review"},
    )

    assert len(result.raw_output["defense_questions"]) == 2
    assert result.raw_output["defense_questions"][0]["risk_level"] == "high"
    assert result.findings[0].title == "Defense needs baseline justification"
    assert agent.handoff_summary(result) == "Two defense questions need priority preparation."
    assert '"minimum_question_count": 8' in llm_service.requests[0].user_prompt
    assert "do not invent external evidence" in llm_service.requests[0].user_prompt


def test_defense_preparation_agent_handles_missing_prior_findings() -> None:
    llm_service = FakeLLMService('{"defense_questions": [], "findings": []}')
    agent = DefensePreparationAgent(llm_service=llm_service)

    result = agent.run_review(previous_agent_findings=[], review_type="defense_preparation")

    assert result.raw_output["defense_questions"] == []
    assert result.raw_output["handoff_summary"] == "Prepared 0 defense questions. High-risk questions: 0."
    assert '"missing_previous_findings": true' in llm_service.requests[0].user_prompt
    assert '"minimum_question_count": 3' in llm_service.requests[0].user_prompt


def test_defense_preparation_agent_saves_findings(db: Session) -> None:
    response_text = """{
        "defense_questions": [
            {
                "question": "Why is the research gap defensible?",
                "category": "research_gap",
                "risk_level": "high",
                "suggested_answer_points": ["Tie the gap to literature findings."]
            }
        ],
        "findings": [
            {
                "category": "defense",
                "severity": "medium",
                "title": "Prepare gap defense",
                "description": "The gap needs a clear defense answer.",
                "evidence": {"field": "research_gap"},
                "recommendation": "Draft a short evidence-backed response."
            }
        ]
    }"""
    records = seed_run_records(db)
    analysis_run_id: UUID = records["analysis_run"].id
    agent_id: UUID = records["agent"].id
    project: ThesisProject = records["project"]
    agent = DefensePreparationAgent(llm_service=FakeLLMService(response_text))

    result = agent.run_and_save(
        db,
        analysis_run_id=analysis_run_id,
        agent_id=agent_id,
        previous_agent_findings=[{"title": "Gap lacks support"}],
        project_context={"title": project.title, "research_gap": project.research_gap},
    )

    findings = db.scalars(select(AgentFinding)).all()

    assert len(result.findings) == 1
    assert len(findings) == 1
    assert findings[0].analysis_run_id == analysis_run_id
    assert findings[0].agent_id == agent_id
    assert findings[0].title == "Prepare gap defense"
    assert findings[0].evidence == {"field": "research_gap"}
