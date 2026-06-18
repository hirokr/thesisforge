from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.base import AgentExecutionError, AgentFindingOutput, AgentRunResult
from app.db.base import Base
from app.models import Agent, AgentMessage, AnalysisRun, Document, DocumentChunk, Reference, Report, ThesisProject, UserProfile
from app.seeds.agents import DEFAULT_AGENTS
from app.services.thesis_review_workflow import ThesisReviewWorkflow, WorkflowOptions
from app.services.llm_service import LLMAuthenticationError
from app.services.thesis_review_workflow import ThesisReviewWorkflowError


class FakeBandService:
    def __init__(self) -> None:
        self.created_chats: list[dict[str, Any]] = []
        self.sent_messages: list[dict[str, Any]] = []

    def create_chat(self, task_id: str, metadata: dict[str, Any] | None = None) -> dict[str, str]:
        self.created_chats.append({"task_id": task_id, "metadata": metadata})
        return {"id": "band-chat-id"}

    def send_message(self, chat_id: str, content: str, mentions: list[dict[str, Any]] | None = None) -> dict[str, str]:
        self.sent_messages.append({"chat_id": chat_id, "content": content, "mentions": mentions})
        return {"id": f"band-message-{len(self.sent_messages)}"}


class FakeReviewAgent:
    def __init__(self, slug: str, *, should_fail: bool = False, failure: Exception | None = None) -> None:
        self.slug = slug
        self.should_fail = should_fail
        self.failure = failure
        self.calls: list[dict[str, Any]] = []

    def run_and_save(self, db: Session, **kwargs: Any) -> AgentRunResult:
        self.calls.append(kwargs)
        if self.failure is not None:
            raise AgentExecutionError(f"{self.slug} failed") from self.failure
        if self.should_fail:
            raise AgentExecutionError(f"{self.slug} failed")

        return AgentRunResult(
            agent_name=self.slug,
            agent_slug=self.slug,
            text="{}",
            raw_output={
                "handoff_summary": f"{self.slug} finished",
                "defense_questions": [{"question": "Why this method?", "category": "methodology", "risk_level": "high"}]
                if self.slug == "defense-preparation"
                else [],
                "citation_checks": [],
            },
            findings=[
                AgentFindingOutput(
                    category=self.slug,
                    severity="medium",
                    title=f"{self.slug} finding",
                    description=f"{self.slug} description",
                )
            ],
            provider="openai",
            model="gpt-test",
        )

    def handoff_summary(self, result: AgentRunResult) -> str:
        return str(result.raw_output["handoff_summary"])


class FakeReportAgent:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def run_and_save(self, db: Session, **kwargs: Any) -> tuple[AgentRunResult, Report]:
        self.calls.append(kwargs)
        project: ThesisProject = kwargs["project"]
        analysis_run: AnalysisRun = kwargs["analysis_run"]
        report = Report(
            project_id=project.id,
            analysis_run_id=analysis_run.id,
            title="Thesis Health Report",
            status="completed",
            overall_score=88,
            executive_summary="Workflow completed.",
            content="# Thesis Health Report",
            structured_report={"partial_failures": kwargs["partial_failures"]},
        )
        analysis_run.summary = "Workflow completed."
        analysis_run.overall_score = 88
        project.latest_score = 88
        db.add(report)
        db.commit()
        db.refresh(report)
        return (
            AgentRunResult(
                agent_name="report-generator",
                agent_slug="report-generator",
                text="{}",
                raw_output={"overall_score": 88, "handoff_summary": "report finished"},
                findings=[],
                provider="openai",
                model="gpt-test",
            ),
            report,
        )


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db
    Base.metadata.drop_all(engine)


def seed_workflow_records(db: Session) -> AnalysisRun:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(
        owner=owner,
        title="Agentic Thesis Review",
        research_area="AI-assisted research",
        problem_statement="Students need structured thesis quality checks.",
        research_gap="Existing tools do not coordinate specialized review agents.",
        objectives="Build a coordinated thesis review workflow.",
        methodology_summary="Use specialized LLM agents with handoffs.",
        dataset_summary="Demo thesis drafts and references.",
        results_summary="Early tests show clearer revision priorities.",
    )
    run = AnalysisRun(project=project, status="queued")
    document = Document(project=project, filename="draft.txt", document_type="thesis_draft", parse_status="parsed", raw_text="Intro")
    chunk = DocumentChunk(document=document, chunk_index=0, content="The thesis proposes a coordinated review workflow.")
    reference = Reference(project=project, document=document, citation_key="smith2025", title="Agentic review", authors=["Smith"], year=2025)
    agents = [
        Agent(
            name=default.name,
            slug=default.slug,
            description=default.description,
            system_prompt=default.system_prompt,
            default_model_provider=default.default_model_provider,
            default_model_name=default.default_model_name,
            temperature=default.temperature,
            is_active=default.is_active,
        )
        for default in DEFAULT_AGENTS
    ]
    db.add_all([owner, project, run, document, chunk, reference, *agents])
    db.commit()
    db.refresh(run)
    return run


def build_workflow(*, failing_slug: str | None = None) -> tuple[ThesisReviewWorkflow, dict[str, FakeReviewAgent], FakeReportAgent, FakeBandService]:
    review_slugs = [
        "literature-review",
        "research-gap",
        "citation",
        "methodology-consistency",
        "results-interpretation",
        "defense-preparation",
    ]
    review_agents = {slug: FakeReviewAgent(slug, should_fail=slug == failing_slug) for slug in review_slugs}
    report_agent = FakeReportAgent()
    band_service = FakeBandService()
    factories = {slug: (lambda record, agent=agent: agent) for slug, agent in review_agents.items()}
    factories["report-generator"] = lambda record: report_agent
    workflow = ThesisReviewWorkflow(agent_factories=factories, band_service=band_service)  # type: ignore[arg-type]
    return workflow, review_agents, report_agent, band_service


def test_thesis_review_workflow_runs_agents_in_order_and_records_handoffs(db: Session) -> None:
    run = seed_workflow_records(db)
    workflow, review_agents, report_agent, band_service = build_workflow()

    result = workflow.run(db, analysis_run_id=run.id)
    saved_run = db.get(AnalysisRun, run.id)
    messages = db.scalars(select(AgentMessage).order_by(AgentMessage.created_at)).all()

    assert saved_run is not None
    assert saved_run.status == "completed"
    assert saved_run.overall_score == 88
    assert result.report is not None
    assert list(result.agent_results) == [
        "literature-review",
        "research-gap",
        "citation",
        "methodology-consistency",
        "results-interpretation",
        "defense-preparation",
        "report-generator",
    ]
    assert [message.task for message in messages] == [
        "literature-review_to_research-gap",
        "research-gap_to_citation",
        "citation_to_methodology-consistency",
        "methodology-consistency_to_results-interpretation",
        "results-interpretation_to_defense-preparation",
        "defense-preparation_to_report-generator",
    ]
    assert {message.status for message in messages} == {"sent"}
    assert len(band_service.sent_messages) == 6
    assert len(report_agent.calls[0]["agent_findings"]) == 6
    assert report_agent.calls[0]["partial_failures"] == []
    assert review_agents["research-gap"].calls[0]["literature_findings"][0]["category"] == "literature-review"


def test_thesis_review_workflow_continues_after_non_report_agent_failure(db: Session) -> None:
    run = seed_workflow_records(db)
    workflow, review_agents, report_agent, _band_service = build_workflow(failing_slug="citation")

    result = workflow.run(db, analysis_run_id=run.id, options=WorkflowOptions(use_band=False))
    saved_run = db.get(AnalysisRun, run.id)
    messages = db.scalars(select(AgentMessage).order_by(AgentMessage.created_at)).all()

    assert saved_run is not None
    assert saved_run.status == "completed"
    assert result.report is not None
    assert [failure.agent_slug for failure in result.partial_failures] == ["citation"]
    assert report_agent.calls[0]["partial_failures"] == [{"agent_slug": "citation", "message": "citation failed"}]
    assert "citation" not in result.agent_results
    assert review_agents["methodology-consistency"].calls
    assert any(message.message_type == "agent_failure" and message.status == "failed" for message in messages)
    assert all(message.task != "citation_to_methodology-consistency" for message in messages)


def test_thesis_review_workflow_stops_after_provider_authentication_failure(db: Session) -> None:
    run = seed_workflow_records(db)
    workflow, review_agents, _report_agent, _band_service = build_workflow()
    review_agents["literature-review"].failure = LLMAuthenticationError(
        "OpenAI authentication failed. Check OPENAI_API_KEY."
    )

    with pytest.raises(ThesisReviewWorkflowError, match="OpenAI authentication failed"):
        workflow.run(db, analysis_run_id=run.id, options=WorkflowOptions(use_band=False))

    assert not review_agents["research-gap"].calls
    messages = db.scalars(select(AgentMessage).order_by(AgentMessage.created_at)).all()
    assert [message.task for message in messages] == ["literature-review_failed"]
