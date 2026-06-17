from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AgentMessage
from app.services.band_service import BandService, BandServiceError


@dataclass(frozen=True)
class AgentMessageCreate:
    analysis_run_id: UUID
    project_id: UUID
    message_type: str
    summary: str
    from_agent_id: UUID | None = None
    to_agent_id: UUID | None = None
    task: str | None = None
    payload: dict[str, Any] | None = None
    content: str | None = None
    mentions: list[Mapping[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] | None = None


def create_local_agent_message(
    db: Session,
    message: AgentMessageCreate,
    *,
    status: str = "pending",
    band_message_id: str | None = None,
) -> AgentMessage:
    record = AgentMessage(
        analysis_run_id=message.analysis_run_id,
        project_id=message.project_id,
        agent_id=message.from_agent_id,
        from_agent_id=message.from_agent_id,
        to_agent_id=message.to_agent_id,
        role="agent",
        content=message.content or message.summary,
        message_type=message.message_type,
        task=message.task,
        summary=message.summary,
        payload=message.payload,
        band_message_id=band_message_id,
        status=status,
        extra_metadata=message.metadata,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def send_agent_message_via_band(
    db: Session,
    *,
    band_service: BandService,
    chat_id: str,
    message: AgentMessageCreate,
) -> AgentMessage:
    record = create_local_agent_message(db, message, status="pending")
    try:
        response = band_service.send_message(
            chat_id,
            message.content or message.summary,
            mentions=list(message.mentions) if message.mentions else None,
        )
    except BandServiceError:
        record.status = "failed"
        db.commit()
        db.refresh(record)
        return record

    record.status = "sent"
    record.band_message_id = _response_id(response)
    db.commit()
    db.refresh(record)
    return record


def post_agent_event_via_band(
    db: Session,
    *,
    band_service: BandService,
    chat_id: str,
    message: AgentMessageCreate,
) -> AgentMessage:
    record = create_local_agent_message(db, message, status="pending")
    try:
        response = band_service.post_event(
            chat_id,
            message.content or message.summary,
            message_type=message.message_type,
            metadata=message.metadata,
        )
    except BandServiceError:
        record.status = "failed"
        db.commit()
        db.refresh(record)
        return record

    record.status = "sent"
    record.band_message_id = _response_id(response)
    db.commit()
    db.refresh(record)
    return record


def _response_id(response: Mapping[str, Any]) -> str | None:
    value = response.get("id")
    return str(value) if value is not None else None
