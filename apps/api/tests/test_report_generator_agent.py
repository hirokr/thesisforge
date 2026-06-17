from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.report_generator import ReportGeneratorAgent
from app.db.base import Base
from app.models import ActionTask, AnalysisRun, Report, ThesisProject, UserProfile
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
        research_area="AI-assisted research",
    )
    analysis_run = AnalysisRun(project=project, status="running")
    db.add_all([owner, project, analysis_run])
    db.commit()
    return {"project": project, "analysis_run": analysis_run}


def test_report_generator_agent_outputs_expected_sections() -> None:
    response_text = """{
        "overall_score": 76,
        "score_breakdown": {"gap": 70, "citation": 80, "methodology": 72, "results": 78, "defense": 75},
        "executive_summary": "The thesis is promising but needs stronger baseline and citation support.",
        "major_risks": ["Baseline comparison may be challenged.", "Some claims have weak citation support."],
        "priority_fixes": [
            {
                "title": "Add a baseline comparison",
                "category": "methodology",
                "priority": "high",
                "description": "Compare against a single-agent or manual review baseline."
            }
        ],
        "defense_questions": [
            {
                "question": "Why is the multi-agent workflow necessary?",
                "category": "methodology",
                "risk_level": "high",
                "suggested_answer_points": ["Explain role specialization."]
            }
        ],
        "markdown_report": "# Thesis Health Report\\n\\nThe thesis needs a baseline.",
        "structured_report": {"status": "ready", "priority_fix_count": 1},
        "partial_failures": []
    }"""
    llm_service = FakeLLMService(response_text)
    agent = ReportGeneratorAgent(llm_service=llm_service)

    result = agent.run_review(
        project_metadata={"title": "Agentic Thesis Review"},
        agent_findings=[{"category": "methodology", "severity": "high", "title": "Missing baseline"}],
        citation_checks=[{"claim_text": "Workflow improves feedback", "status": "weak"}],
        agent_messages=[{"role": "assistant", "summary": "Methodology handoff"}],
        defense_questions=[{"question": "Why this workflow?", "risk_level": "high"}],
    )

    assert result.raw_output["overall_score"] == 76
    assert result.raw_output["score_breakdown"]["gap"] == 70
    assert result.raw_output["priority_fixes"][0]["title"] == "Add a baseline comparison"
    assert "Return both markdown_report and structured_report" in llm_service.requests[0].user_prompt


def test_report_generator_agent_handles_partial_failures_and_defaults() -> None:
    llm_service = FakeLLMService('{"overall_score": null, "priority_fixes": ["Upload references"], "partial_failures": ["citation-agent"]}')
    agent = ReportGeneratorAgent(llm_service=llm_service)

    result = agent.run_review(
        project_metadata={"title": "Partial Review"},
        agent_findings=[],
        partial_failures=["citation-agent"],
    )

    assert result.raw_output["score_breakdown"] == {}
    assert result.raw_output["major_risks"] == []
    assert result.raw_output["structured_report"]["priority_fixes"] == ["Upload references"]
    assert result.raw_output["markdown_report"].startswith("# Thesis Health Report")
    assert '"has_partial_failures": true' in llm_service.requests[0].user_prompt


def test_report_generator_agent_saves_report_and_priority_tasks(db: Session) -> None:
    response_text = """{
        "overall_score": 82,
        "score_breakdown": {"gap": 84, "citation": 78},
        "executive_summary": "The thesis is defensible after targeted citation updates.",
        "major_risks": ["Citation support is uneven."],
        "priority_fixes": [
            {
                "title": "Strengthen citation support",
                "category": "citation",
                "priority": "urgent",
                "description": "Add references for unsupported claims."
            },
            "Clarify limitations"
        ],
        "defense_questions": [],
        "markdown_report": "# Thesis Health Report\\n\\nScore: 82",
        "structured_report": {"overall_score": 82, "priority_fix_count": 2}
    }"""
    records = seed_run_records(db)
    project: ThesisProject = records["project"]
    analysis_run: AnalysisRun = records["analysis_run"]
    agent = ReportGeneratorAgent(llm_service=FakeLLMService(response_text))

    result, report = agent.run_and_save(
        db,
        project=project,
        analysis_run=analysis_run,
        project_metadata={"title": project.title, "research_area": project.research_area},
        agent_findings=[{"title": "Weak citation support"}],
    )
    tasks = db.scalars(select(ActionTask).order_by(ActionTask.created_at)).all()
    saved_report = db.scalar(select(Report).where(Report.id == report.id))

    assert result.raw_output["overall_score"] == 82
    assert saved_report is not None
    assert saved_report.status == "completed"
    assert saved_report.overall_score == 82
    assert saved_report.score_breakdown == {"gap": 84, "citation": 78}
    assert saved_report.executive_summary == "The thesis is defensible after targeted citation updates."
    assert saved_report.content == "# Thesis Health Report\n\nScore: 82"
    assert saved_report.structured_report == {"overall_score": 82, "priority_fix_count": 2}
    assert len(tasks) == 2
    assert tasks[0].report_id == report.id
    assert tasks[0].priority == "urgent"
    assert tasks[0].category == "citation"
    assert tasks[1].title == "Clarify limitations"
    assert project.latest_score == 82
    assert analysis_run.overall_score == 82
