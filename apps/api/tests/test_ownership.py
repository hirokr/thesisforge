from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser
from app.db.base import Base
from app.models import ActionTask, AnalysisRun, Document, Report, ThesisProject, UserProfile
from app.services.ownership import (
    PROJECT_RELATED_NOT_FOUND,
    reject_owner_id_update,
    require_owned_action_task,
    require_owned_analysis_run,
    require_owned_document,
    require_owned_project,
    require_owned_report,
)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


def seed_owned_graph(db: Session) -> dict[str, UUID]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com", full_name="Owner")
    other_user = UserProfile(auth_user_id="auth-other", email="other@example.com", full_name="Other")
    db.add_all([owner, other_user])
    db.flush()

    project = ThesisProject(owner_id=owner.id, title="Owned thesis")
    other_project = ThesisProject(owner_id=other_user.id, title="Other thesis")
    db.add_all([project, other_project])
    db.flush()

    document = Document(project_id=project.id, filename="draft.txt")
    other_document = Document(project_id=other_project.id, filename="other.txt")
    analysis_run = AnalysisRun(project_id=project.id)
    report = Report(project_id=project.id, title="Review report")
    task = ActionTask(project_id=project.id, title="Revise literature review")
    db.add_all([document, other_document, analysis_run, report, task])
    db.commit()

    return {
        "project_id": project.id,
        "other_project_id": other_project.id,
        "document_id": document.id,
        "other_document_id": other_document.id,
        "analysis_run_id": analysis_run.id,
        "report_id": report.id,
        "task_id": task.id,
    }


def auth_user(auth_user_id: str = "auth-owner") -> AuthenticatedUser:
    return AuthenticatedUser(auth_user_id=auth_user_id, email=f"{auth_user_id}@example.com")


def assert_safe_404(exc_info: pytest.ExceptionInfo[HTTPException]) -> None:
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == PROJECT_RELATED_NOT_FOUND


def test_require_owned_project_returns_project_for_owner(db: Session) -> None:
    ids = seed_owned_graph(db)

    project = require_owned_project(db, auth_user(), ids["project_id"])

    assert project.id == ids["project_id"]
    assert project.title == "Owned thesis"


def test_require_owned_project_hides_other_users_project(db: Session) -> None:
    ids = seed_owned_graph(db)

    with pytest.raises(HTTPException) as exc_info:
        require_owned_project(db, auth_user(), ids["other_project_id"])

    assert_safe_404(exc_info)


def test_require_owned_document_checks_parent_project_owner(db: Session) -> None:
    ids = seed_owned_graph(db)

    document = require_owned_document(db, auth_user(), ids["document_id"])

    assert document.id == ids["document_id"]

    with pytest.raises(HTTPException) as exc_info:
        require_owned_document(db, auth_user(), ids["other_document_id"])

    assert_safe_404(exc_info)


def test_require_owned_analysis_report_and_task_check_project_owner(db: Session) -> None:
    ids = seed_owned_graph(db)

    assert require_owned_analysis_run(db, auth_user(), ids["analysis_run_id"]).id == ids["analysis_run_id"]
    assert require_owned_report(db, auth_user(), ids["report_id"]).id == ids["report_id"]
    assert require_owned_action_task(db, auth_user(), ids["task_id"]).id == ids["task_id"]

    with pytest.raises(HTTPException) as exc_info:
        require_owned_report(db, auth_user("auth-other"), ids["report_id"])

    assert_safe_404(exc_info)


def test_missing_user_profile_returns_safe_404(db: Session) -> None:
    ids = seed_owned_graph(db)

    with pytest.raises(HTTPException) as exc_info:
        require_owned_project(db, auth_user("auth-missing"), ids["project_id"])

    assert_safe_404(exc_info)


def test_reject_owner_id_update_blocks_owner_mutation() -> None:
    with pytest.raises(HTTPException) as exc_info:
        reject_owner_id_update({"title": "Updated", "owner_id": "other-user"})

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Project ownership cannot be changed."
