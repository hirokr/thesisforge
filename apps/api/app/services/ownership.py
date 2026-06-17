from uuid import UUID
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import ActionTask, AnalysisRun, Document, Report, ThesisProject, UserProfile


PROJECT_RELATED_NOT_FOUND = "Resource not found."
OwnedResource = TypeVar("OwnedResource")


def safe_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PROJECT_RELATED_NOT_FOUND)


def get_profile_for_auth_user(db: Session, current_user: AuthenticatedUser) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.auth_user_id == current_user.auth_user_id))


def require_profile_for_auth_user(db: Session, current_user: AuthenticatedUser) -> UserProfile:
    profile = get_profile_for_auth_user(db, current_user)
    if profile is None:
        raise safe_not_found()
    return profile


def require_owned_project(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> ThesisProject:
    profile = require_profile_for_auth_user(db, current_user)
    project = db.scalar(select(ThesisProject).where(ThesisProject.id == project_id, ThesisProject.owner_id == profile.id))
    if project is None:
        raise safe_not_found()
    return project


def require_owned_document(db: Session, current_user: AuthenticatedUser, document_id: UUID) -> Document:
    document = _require_owned_resource(
        db,
        current_user,
        select(Document).join(ThesisProject).where(Document.id == document_id),
    )
    return document


def require_owned_analysis_run(db: Session, current_user: AuthenticatedUser, analysis_run_id: UUID) -> AnalysisRun:
    analysis_run = _require_owned_resource(
        db,
        current_user,
        select(AnalysisRun).join(ThesisProject).where(AnalysisRun.id == analysis_run_id),
    )
    return analysis_run


def require_owned_report(db: Session, current_user: AuthenticatedUser, report_id: UUID) -> Report:
    report = _require_owned_resource(
        db,
        current_user,
        select(Report).join(ThesisProject).where(Report.id == report_id),
    )
    return report


def require_owned_action_task(db: Session, current_user: AuthenticatedUser, task_id: UUID) -> ActionTask:
    task = _require_owned_resource(
        db,
        current_user,
        select(ActionTask).join(ThesisProject).where(ActionTask.id == task_id),
    )
    return task


def reject_owner_id_update(payload: object) -> None:
    if isinstance(payload, dict) and "owner_id" in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project ownership cannot be changed.")
    if hasattr(payload, "owner_id"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project ownership cannot be changed.")


def _require_owned_resource(
    db: Session,
    current_user: AuthenticatedUser,
    statement: Select[tuple[OwnedResource]],
) -> OwnedResource:
    profile = require_profile_for_auth_user(db, current_user)
    resource = db.scalar(statement.where(ThesisProject.owner_id == profile.id))
    if resource is None:
        raise safe_not_found()
    return resource
