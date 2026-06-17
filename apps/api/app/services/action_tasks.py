from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import ActionTask
from app.schemas.action_task import ActionTaskUpdate
from app.services.ownership import require_owned_action_task, require_owned_project


def list_project_tasks(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> list[ActionTask]:
    project = require_owned_project(db, current_user, project_id)
    return list(
        db.scalars(
            select(ActionTask)
            .where(ActionTask.project_id == project.id)
            .order_by(ActionTask.created_at.desc(), ActionTask.updated_at.desc())
        )
    )


def update_task(db: Session, current_user: AuthenticatedUser, task_id: UUID, payload: ActionTaskUpdate) -> ActionTask:
    task = require_owned_action_task(db, current_user, task_id)
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, current_user: AuthenticatedUser, task_id: UUID) -> None:
    task = require_owned_action_task(db, current_user, task_id)
    db.delete(task)
    db.commit()
