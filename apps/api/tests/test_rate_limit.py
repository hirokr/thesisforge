from collections.abc import Generator
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.rate_limit import clear_rate_limit_state
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
def clear_app_state() -> Generator[None, None, None]:
    app.dependency_overrides.clear()
    clear_rate_limit_state()
    yield
    clear_rate_limit_state()
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


def seed_project(db: Session) -> ThesisProject:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    db.add(owner)
    db.flush()
    project = ThesisProject(owner_id=owner.id, title="Rate limited project")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def low_limit_settings() -> SimpleNamespace:
    return SimpleNamespace(
        rate_limit_window_seconds=60,
        rate_limit_file_uploads_per_window=1,
        rate_limit_analysis_runs_per_window=1,
    )


def test_text_document_route_returns_friendly_rate_limit(monkeypatch, db: Session, caplog) -> None:
    monkeypatch.setattr("app.core.rate_limit.get_settings", low_limit_settings)
    project = seed_project(db)
    client = client_for(db)

    first_response = client.post(
        f"/api/v1/projects/{project.id}/documents/text",
        json={"document_type": "thesis_draft", "title": "Draft", "raw_text": "Short thesis text."},
    )
    second_response = client.post(
        f"/api/v1/projects/{project.id}/documents/text",
        json={"document_type": "thesis_draft", "title": "Draft 2", "raw_text": "More thesis text."},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 429
    assert second_response.json()["message"] == "Too many requests. Please wait a moment and try again."
    assert second_response.headers["Retry-After"] == "60"
    assert "user_id=auth-owner" in caplog.text
    assert "ip=testclient" in caplog.text


def test_analysis_run_route_is_rate_limited(monkeypatch, db: Session) -> None:
    monkeypatch.setattr("app.core.rate_limit.get_settings", low_limit_settings)
    monkeypatch.setattr(
        "app.api.v1.routes.analysis_runs.enqueue_analysis_run",
        lambda analysis_run, **kwargs: "job-id",
    )
    project = seed_project(db)
    client = client_for(db)

    first_response = client.post(f"/api/v1/projects/{project.id}/analysis-runs")
    second_response = client.post(f"/api/v1/projects/{project.id}/analysis-runs")

    assert first_response.status_code == 201
    assert second_response.status_code == 429
    assert second_response.json()["code"] == "http_429"
