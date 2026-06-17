from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import SupervisorFeedback
from app.schemas.supervisor_feedback import SupervisorFeedbackCreate
from app.services.ownership import require_owned_project


def create_supervisor_feedback(
    db: Session,
    current_user: AuthenticatedUser,
    project_id: UUID,
    payload: SupervisorFeedbackCreate,
) -> SupervisorFeedback:
    project = require_owned_project(db, current_user, project_id)
    feedback = SupervisorFeedback(
        project_id=project.id,
        feedback_text=payload.feedback_text,
        source=payload.source,
        feedback_date=payload.feedback_date,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def list_supervisor_feedback(
    db: Session,
    current_user: AuthenticatedUser,
    project_id: UUID,
) -> list[SupervisorFeedback]:
    project = require_owned_project(db, current_user, project_id)
    return list(
        db.scalars(
            select(SupervisorFeedback)
            .where(SupervisorFeedback.project_id == project.id)
            .order_by(SupervisorFeedback.feedback_date.desc().nullslast(), SupervisorFeedback.created_at.desc())
        )
    )
