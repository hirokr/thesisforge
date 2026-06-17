from collections.abc import Generator
from pathlib import Path
from types import SimpleNamespace
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
from app.models import Document, DocumentChunk, Reference, ThesisProject


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


def client_for(db: Session) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        auth_user_id="auth-owner",
        email="owner@example.com",
    )
    return TestClient(app)


def test_load_demo_project_creates_review_ready_data(
    db: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.services.demo.get_settings", lambda: SimpleNamespace(upload_storage_dir=str(tmp_path)))
    client = client_for(db)

    response = client.post("/api/v1/demo/project")

    assert response.status_code == 201
    body = response.json()
    assert body["project"]["title"] == "Interpretable Energy Demand Forecasting for Mid-Sized University Buildings"
    assert body["project"]["problem_statement"]
    assert body["project"]["research_gap"]
    assert body["project"]["methodology_summary"]
    assert body["project"]["results_summary"]
    assert body["document_count"] == 3
    assert body["reference_count"] >= 3

    project_id = UUID(body["project"]["id"])
    project = db.scalar(select(ThesisProject).where(ThesisProject.id == project_id))
    documents = list(db.scalars(select(Document).where(Document.project_id == project_id)))
    references = list(db.scalars(select(Reference).where(Reference.project_id == project_id)))
    draft = next(document for document in documents if document.document_type == "thesis_draft")
    results = next(document for document in documents if document.document_type == "results_file")

    assert project is not None
    assert {document.document_type for document in documents} == {"thesis_draft", "reference_file", "results_file"}
    assert draft.parse_status == "parsed"
    assert db.scalar(select(DocumentChunk).where(DocumentChunk.document_id == draft.id)) is not None
    assert references[0].citation_key
    assert results.parse_status == "parsed"
    assert results.parse_metadata["row_count"] == 4
