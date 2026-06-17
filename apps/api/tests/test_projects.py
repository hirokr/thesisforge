from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import ThesisProject, UserProfile


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None, None, None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def client_for(db: Session, auth_user_id: str = "auth-owner") -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        auth_user_id=auth_user_id,
        email=f"{auth_user_id}@example.com",
    )
    return TestClient(app)


def test_create_and_list_projects_for_current_user(db: Session) -> None:
    client = client_for(db)

    create_response = client.post(
        "/api/v1/projects",
        json={
            "title": "Explainable AI Thesis",
            "research_area": "Machine learning",
            "thesis_stage": "proposal",
            "problem_statement": "Review thesis quality consistently.",
        },
    )
    list_response = client.get("/api/v1/projects")

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Explainable AI Thesis"
    assert created["status"] == "draft"
    assert created["problem_statement"] == "Review thesis quality consistently."
    assert list_response.status_code == 200
    assert [project["id"] for project in list_response.json()] == [created["id"]]


def test_get_patch_and_delete_owned_project(db: Session) -> None:
    client = client_for(db)
    created = client.post("/api/v1/projects", json={"title": "Initial title"}).json()

    get_response = client.get(f"/api/v1/projects/{created['id']}")
    patch_response = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"title": "Updated title", "results_summary": "Early results are promising."},
    )
    delete_response = client.delete(f"/api/v1/projects/{created['id']}")
    missing_response = client.get(f"/api/v1/projects/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Initial title"
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Updated title"
    assert patch_response.json()["results_summary"] == "Early results are promising."
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


def test_project_routes_hide_other_users_projects(db: Session) -> None:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    other = UserProfile(auth_user_id="auth-other", email="other@example.com")
    db.add_all([owner, other])
    db.flush()
    project = ThesisProject(owner_id=other.id, title="Other project")
    db.add(project)
    db.commit()
    db.refresh(project)

    client = client_for(db, "auth-owner")

    assert client.get(f"/api/v1/projects/{project.id}").status_code == 404
    assert client.patch(f"/api/v1/projects/{project.id}", json={"title": "Blocked"}).status_code == 404
    assert client.delete(f"/api/v1/projects/{project.id}").status_code == 404
    assert client.get("/api/v1/projects").json() == []


def test_project_update_rejects_owner_id_payload(db: Session) -> None:
    client = client_for(db)
    created = client.post("/api/v1/projects", json={"title": "Immutable owner"}).json()

    response = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"owner_id": "dbe237d8-f449-40b1-814b-1a8f68efafbd"},
    )
    project = db.scalar(select(ThesisProject).where(ThesisProject.id == UUID(created["id"])))

    assert response.status_code == 422
    assert project is not None
    assert project.title == "Immutable owner"
