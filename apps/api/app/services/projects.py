from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import ThesisProject
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.ownership import reject_owner_id_update, require_owned_project
from app.services.user_profiles import get_or_create_user_profile


def create_project(db: Session, current_user: AuthenticatedUser, payload: ProjectCreate) -> ThesisProject:
    profile = get_or_create_user_profile(db, current_user)
    project = ThesisProject(owner_id=profile.id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, current_user: AuthenticatedUser) -> list[ThesisProject]:
    profile = get_or_create_user_profile(db, current_user)
    return list(
        db.scalars(
            select(ThesisProject)
            .where(ThesisProject.owner_id == profile.id)
            .order_by(ThesisProject.updated_at.desc(), ThesisProject.created_at.desc())
        )
    )


def get_project(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> ThesisProject:
    return require_owned_project(db, current_user, project_id)


def update_project(
    db: Session,
    current_user: AuthenticatedUser,
    project_id: UUID,
    payload: ProjectUpdate,
) -> ThesisProject:
    reject_owner_id_update(payload)
    project = require_owned_project(db, current_user, project_id)
    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(project, field_name, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> None:
    project = require_owned_project(db, current_user, project_id)
    db.delete(project)
    db.commit()
