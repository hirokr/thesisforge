from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.supervisor_feedback import SupervisorFeedbackCreate, SupervisorFeedbackRead
from app.services.supervisor_feedback import create_supervisor_feedback, list_supervisor_feedback

router = APIRouter(prefix="/projects/{project_id}/feedback", tags=["supervisor-feedback"])


@router.post("", response_model=SupervisorFeedbackRead, status_code=status.HTTP_201_CREATED)
def create_supervisor_feedback_route(
    project_id: UUID,
    payload: SupervisorFeedbackCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SupervisorFeedbackRead:
    return create_supervisor_feedback(db, current_user, project_id, payload)


@router.get("", response_model=list[SupervisorFeedbackRead])
def list_supervisor_feedback_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SupervisorFeedbackRead]:
    return list_supervisor_feedback(db, current_user, project_id)
