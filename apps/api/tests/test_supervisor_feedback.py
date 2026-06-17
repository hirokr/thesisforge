from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import SupervisorFeedback, ThesisProject, UserProfile


def make_db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


def test_create_and_list_supervisor_feedback_for_owned_project() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        project = seed_project(db)
        client = client_for(db)

        create_response = client.post(
            f"/api/v1/projects/{project.id}/feedback",
            json={
                "feedback_text": "The methodology needs clearer baseline comparisons.",
                "source": "meeting",
                "feedback_date": "2026-06-17T09:30:00+00:00",
            },
        )
        list_response = client.get(f"/api/v1/projects/{project.id}/feedback")

        assert create_response.status_code == 201
        created = create_response.json()
        assert created["project_id"] == str(project.id)
        assert created["feedback_text"] == "The methodology needs clearer baseline comparisons."
        assert created["source"] == "meeting"
        assert created["feedback_date"] == "2026-06-17T09:30:00"
        assert created["status"] == "new"
        assert "created_at" in created
        assert "updated_at" in created
        assert list_response.status_code == 200
        assert [item["id"] for item in list_response.json()] == [created["id"]]
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_supervisor_feedback_defaults_to_manual_source() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        project = seed_project(db)
        client = client_for(db)

        response = client.post(f"/api/v1/projects/{project.id}/feedback", json={"feedback_text": "Add limitations section."})
        feedback = db.scalar(select(SupervisorFeedback))

        assert response.status_code == 201
        assert response.json()["source"] == "manual"
        assert feedback is not None
        assert feedback.source == "manual"
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_supervisor_feedback_rejects_empty_text_and_invalid_source() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        project = seed_project(db)
        client = client_for(db)

        empty_response = client.post(f"/api/v1/projects/{project.id}/feedback", json={"feedback_text": ""})
        source_response = client.post(
            f"/api/v1/projects/{project.id}/feedback",
            json={"feedback_text": "Good progress.", "source": "chat"},
        )

        assert empty_response.status_code == 422
        assert source_response.status_code == 422
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_supervisor_feedback_routes_hide_other_users_projects() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        other = UserProfile(auth_user_id="auth-other", email="other@example.com")
        project = ThesisProject(owner=other, title="Other project")
        db.add_all([other, project])
        db.commit()
        db.refresh(project)
        client = client_for(db)

        assert client.get(f"/api/v1/projects/{project.id}/feedback").status_code == 404
        assert client.post(f"/api/v1/projects/{project.id}/feedback", json={"feedback_text": "Hidden"}).status_code == 404
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


def seed_project(db: Session) -> ThesisProject:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Owned project")
    db.add_all([owner, project])
    db.commit()
    db.refresh(project)
    return project
