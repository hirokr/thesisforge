from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.projects import create_project, delete_project, get_project, list_projects, update_project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project_route(
    payload: ProjectCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    return create_project(db, current_user, payload)


@router.get("", response_model=list[ProjectRead])
def list_projects_route(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectRead]:
    return list_projects(db, current_user)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    return get_project(db, current_user, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project_route(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    return update_project(db, current_user, project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    delete_project(db, current_user, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
