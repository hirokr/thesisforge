from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import ActionTask, Report, ThesisProject, UserProfile


def make_db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


def test_list_project_tasks_for_owned_project() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        project, first_task, second_task = seed_tasks(db)
        client = client_for(db)

        response = client.get(f"/api/v1/projects/{project.id}/tasks")

        assert response.status_code == 200
        tasks = response.json()
        assert {task["id"] for task in tasks} == {str(first_task.id), str(second_task.id)}
        assert tasks[0]["title"] in {"Add stronger baseline", "Clarify research gap"}
        assert tasks[0]["project_id"] == str(project.id)
        assert tasks[0]["status"] in {"open", "in_progress"}
        assert tasks[0]["priority"] in {"high", "medium"}
        assert "created_at" in tasks[0]
        assert "updated_at" in tasks[0]
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_patch_task_status() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        _, task, _ = seed_tasks(db)
        client = client_for(db)

        response = client.patch(f"/api/v1/tasks/{task.id}", json={"status": "completed"})
        refreshed_task = db.scalar(select(ActionTask).where(ActionTask.id == task.id))

        assert response.status_code == 200
        assert response.json()["id"] == str(task.id)
        assert response.json()["status"] == "completed"
        assert refreshed_task is not None
        assert refreshed_task.status == "completed"
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_patch_task_rejects_invalid_status() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        _, task, _ = seed_tasks(db)
        client = client_for(db)

        response = client.patch(f"/api/v1/tasks/{task.id}", json={"status": "blocked"})

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_delete_task() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        _, task, _ = seed_tasks(db)
        client = client_for(db)

        response = client.delete(f"/api/v1/tasks/{task.id}")
        deleted_task = db.scalar(select(ActionTask).where(ActionTask.id == task.id))

        assert response.status_code == 204
        assert deleted_task is None
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_task_routes_hide_other_users_tasks() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        other = UserProfile(auth_user_id="auth-other", email="other@example.com")
        project = ThesisProject(owner=other, title="Other project")
        task = ActionTask(project=project, title="Other task", priority="high", status="open")
        db.add_all([other, project, task])
        db.commit()
        db.refresh(project)
        db.refresh(task)
        client = client_for(db)

        assert client.get(f"/api/v1/projects/{project.id}/tasks").status_code == 404
        assert client.patch(f"/api/v1/tasks/{task.id}", json={"status": "dismissed"}).status_code == 404
        assert client.delete(f"/api/v1/tasks/{task.id}").status_code == 404
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def client_for(db: Session, auth_user_id: str = "auth-owner") -> TestClient:
    app.dependency_overrides.clear()

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        auth_user_id=auth_user_id,
        email=f"{auth_user_id}@example.com",
    )
    return TestClient(app)


def seed_tasks(db: Session) -> tuple[ThesisProject, ActionTask, ActionTask]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Owned project")
    report = Report(project=project, title="Thesis Health Report", status="completed")
    first_task = ActionTask(
        project=project,
        report=report,
        title="Add stronger baseline",
        description="Compare against at least one classical baseline.",
        category="methodology",
        priority="high",
        status="open",
    )
    second_task = ActionTask(
        project=project,
        report=report,
        title="Clarify research gap",
        description="Make the gap more specific and evidence-backed.",
        category="research_gap",
        priority="medium",
        status="in_progress",
    )
    db.add_all([owner, project, report, first_task, second_task])
    db.commit()
    db.refresh(project)
    db.refresh(first_task)
    db.refresh(second_task)
    return project, first_task, second_task
