from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Agent, AgentMessage, AnalysisRun, ThesisProject, UserProfile
from app.services.agent_messages import AgentMessageCreate, post_agent_event_via_band, send_agent_message_via_band
from app.services.band_service import BandServiceError


class FakeBandService:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.sent_messages: list[dict[str, object]] = []
        self.events: list[dict[str, object]] = []

    def send_message(self, chat_id: str, content: str, mentions: list[dict[str, object]] | None = None) -> dict[str, str]:
        if self.should_fail:
            raise BandServiceError("Band API request failed.")
        self.sent_messages.append({"chat_id": chat_id, "content": content, "mentions": mentions})
        return {"id": "band-message-id"}

    def post_event(
        self,
        chat_id: str,
        content: str,
        message_type: str = "task",
        metadata: dict[str, object] | None = None,
    ) -> dict[str, str]:
        if self.should_fail:
            raise BandServiceError("Band API request failed.")
        self.events.append({"chat_id": chat_id, "content": content, "message_type": message_type, "metadata": metadata})
        return {"id": "band-event-id"}


def seed_message_records(db: Session) -> dict[str, object]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Agentic Thesis Review")
    run = AnalysisRun(project=project, status="running")
    from_agent = Agent(
        name="Literature Review Agent",
        slug="literature-review",
        description="Reviews literature coverage.",
        system_prompt="Review literature.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    to_agent = Agent(
        name="Research Gap Agent",
        slug="research-gap",
        description="Reviews research gaps.",
        system_prompt="Review gaps.",
        default_model_provider="openai",
        default_model_name="gpt-test",
    )
    db.add_all([owner, project, run, from_agent, to_agent])
    db.commit()
    return {"project": project, "run": run, "from_agent": from_agent, "to_agent": to_agent}


def message_payload(records: dict[str, object]) -> AgentMessageCreate:
    project: ThesisProject = records["project"]  # type: ignore[assignment]
    run: AnalysisRun = records["run"]  # type: ignore[assignment]
    from_agent: Agent = records["from_agent"]  # type: ignore[assignment]
    to_agent: Agent = records["to_agent"]  # type: ignore[assignment]
    return AgentMessageCreate(
        analysis_run_id=run.id,
        project_id=project.id,
        from_agent_id=from_agent.id,
        to_agent_id=to_agent.id,
        message_type="handoff",
        task="validate_research_gap",
        summary="The current gap is too broad.",
        payload={"recommended_focus": "interpretable multimodal reasoning"},
        content="@research_gap_agent The current gap is too broad.",
        mentions=[{"id": "peer-id", "handle": "research_gap_agent"}],
        metadata={"run_id": str(run.id), "project_id": str(project.id)},
    )


def test_send_agent_message_stores_local_sent_record(db: Session) -> None:
    records = seed_message_records(db)
    band_service = FakeBandService()

    record = send_agent_message_via_band(
        db,
        band_service=band_service,  # type: ignore[arg-type]
        chat_id="chat-id",
        message=message_payload(records),
    )
    saved_record = db.scalar(select(AgentMessage).where(AgentMessage.id == record.id))

    assert saved_record is not None
    assert saved_record.status == "sent"
    assert saved_record.band_message_id == "band-message-id"
    assert saved_record.project_id == records["project"].id
    assert saved_record.from_agent_id == records["from_agent"].id
    assert saved_record.to_agent_id == records["to_agent"].id
    assert saved_record.message_type == "handoff"
    assert saved_record.task == "validate_research_gap"
    assert saved_record.summary == "The current gap is too broad."
    assert saved_record.payload == {"recommended_focus": "interpretable multimodal reasoning"}
    assert band_service.sent_messages == [
        {
            "chat_id": "chat-id",
            "content": "@research_gap_agent The current gap is too broad.",
            "mentions": [{"id": "peer-id", "handle": "research_gap_agent"}],
        }
    ]


def test_send_agent_message_marks_local_record_failed_when_band_fails(db: Session) -> None:
    records = seed_message_records(db)
    band_service = FakeBandService(should_fail=True)

    record = send_agent_message_via_band(
        db,
        band_service=band_service,  # type: ignore[arg-type]
        chat_id="chat-id",
        message=message_payload(records),
    )

    assert record.status == "failed"
    assert record.band_message_id is None
    assert db.scalar(select(AgentMessage).where(AgentMessage.id == record.id)) is not None


def test_post_agent_event_stores_local_event_record(db: Session) -> None:
    records = seed_message_records(db)
    band_service = FakeBandService()
    payload = message_payload(records)
    event_payload = AgentMessageCreate(
        analysis_run_id=payload.analysis_run_id,
        project_id=payload.project_id,
        from_agent_id=payload.from_agent_id,
        message_type="task",
        task="citation_check_started",
        summary="Citation Agent started checking claim support.",
        metadata=payload.metadata,
    )

    record = post_agent_event_via_band(
        db,
        band_service=band_service,  # type: ignore[arg-type]
        chat_id="chat-id",
        message=event_payload,
    )

    assert record.status == "sent"
    assert record.band_message_id == "band-event-id"
    assert record.message_type == "task"
    assert band_service.events == [
        {
            "chat_id": "chat-id",
            "content": "Citation Agent started checking claim support.",
            "message_type": "task",
            "metadata": event_payload.metadata,
        }
    ]


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db
    Base.metadata.drop_all(engine)
