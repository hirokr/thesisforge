from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.action_task import ActionTaskRead, ActionTaskUpdate
from app.services.action_tasks import delete_task, list_project_tasks, update_task

router = APIRouter(tags=["action-tasks"])


@router.get("/projects/{project_id}/tasks", response_model=list[ActionTaskRead])
def list_project_tasks_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActionTaskRead]:
    return list_project_tasks(db, current_user, project_id)


@router.patch("/tasks/{task_id}", response_model=ActionTaskRead)
def update_task_route(
    task_id: UUID,
    payload: ActionTaskUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActionTaskRead:
    return update_task(db, current_user, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_route(
    task_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    delete_task(db, current_user, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
