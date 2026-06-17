from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog

ANALYTICS_EVENT_NAMES = {
    "project_created",
    "document_uploaded",
    "analysis_started",
    "analysis_completed",
    "report_viewed",
    "report_copied",
}


def log_analytics_event(
    db: Session,
    *,
    event_name: str,
    project_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    entity_type: str,
    entity_id: UUID | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    if event_name not in ANALYTICS_EVENT_NAMES:
        raise ValueError(f"Unsupported analytics event: {event_name}")

    event = AuditLog(
        project_id=project_id,
        actor_user_id=actor_user_id,
        action=event_name,
        entity_type=entity_type,
        entity_id=entity_id,
        details=_safe_details(details or {}),
    )
    db.add(event)
    return event


def _safe_details(details: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in details.items():
        if value is None or isinstance(value, str | int | float | bool):
            safe[key] = value
        elif isinstance(value, UUID):
            safe[key] = str(value)
    return safe
