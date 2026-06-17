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
from app.models import Document, DocumentChunk, ThesisProject, UserProfile


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


def seed_documents(db: Session) -> dict[str, object]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    other = UserProfile(auth_user_id="auth-other", email="other@example.com")
    db.add_all([owner, other])
    db.flush()

    project = ThesisProject(owner_id=owner.id, title="Owned project")
    other_project = ThesisProject(owner_id=other.id, title="Other project")
    db.add_all([project, other_project])
    db.flush()

    document = Document(
        project_id=project.id,
        filename="draft.txt",
        content_type="text/plain",
        document_type="thesis_draft",
        size_bytes=128,
    )
    other_document = Document(project_id=other_project.id, filename="other.txt")
    db.add_all([document, other_document])
    db.flush()

    chunk = DocumentChunk(document_id=document.id, chunk_index=0, content="Chunk text")
    db.add(chunk)
    db.commit()
    db.refresh(project)
    db.refresh(document)
    db.refresh(other_document)
    db.refresh(chunk)

    return {
        "project": project,
        "document": document,
        "other_document": other_document,
        "chunk": chunk,
    }


def test_list_project_documents_for_owner(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db)

    response = client.get(f"/api/v1/projects/{records['project'].id}/documents")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(records["document"].id)
    assert response.json()[0]["filename"] == "draft.txt"
    assert response.json()[0]["status"] == "uploaded"
    assert response.json()[0]["parse_status"] == "pending"


def test_create_text_document_saves_parsed_document_and_chunks(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db)
    raw_text = "\n\n".join(
        [
            "Introduction\nThis thesis studies multi-agent review workflows.",
            "Methodology\nThe system chunks pasted thesis text before analysis.",
        ]
    )

    response = client.post(
        f"/api/v1/projects/{records['project'].id}/documents/text",
        json={
            "document_type": "thesis_draft",
            "title": "Methodology section",
            "raw_text": raw_text,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == str(records["project"].id)
    assert body["document_type"] == "thesis_draft"
    assert body["title"] == "Methodology section"
    assert body["parse_status"] == "parsed"
    assert body["word_count"] == len(raw_text.split())
    assert body["chunk_count"] == 1

    document = db.scalar(select(Document).where(Document.id == UUID(body["id"])))
    chunks = list(
        db.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == UUID(body["id"]))
            .order_by(DocumentChunk.chunk_index)
        )
    )
    assert document is not None
    assert document.filename == "Methodology section"
    assert document.raw_text == raw_text
    assert document.status == "parsed"
    assert document.parse_status == "parsed"
    assert document.content_type == "text/plain"
    assert document.size_bytes == len(raw_text.encode("utf-8"))
    assert [chunk.chunk_index for chunk in chunks] == [0]
    assert chunks[0].content.startswith("Introduction")


def test_create_text_document_splits_long_text_into_ordered_chunks(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db)
    raw_text = " ".join(f"word{i}" for i in range(720))

    response = client.post(
        f"/api/v1/projects/{records['project'].id}/documents/text",
        json={
            "document_type": "thesis_draft",
            "title": "Long draft",
            "raw_text": raw_text,
        },
    )

    assert response.status_code == 201
    assert response.json()["word_count"] == 720
    assert response.json()["chunk_count"] == 3
    chunks = list(
        db.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == UUID(response.json()["id"]))
            .order_by(DocumentChunk.chunk_index)
        )
    )
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert len(chunks[0].content.split()) == 350
    assert len(chunks[1].content.split()) == 350
    assert len(chunks[2].content.split()) == 20


def test_create_text_document_validates_project_ownership(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db, "auth-other")

    response = client.post(
        f"/api/v1/projects/{records['project'].id}/documents/text",
        json={
            "document_type": "thesis_draft",
            "title": "Blocked",
            "raw_text": "This should not be stored.",
        },
    )

    assert response.status_code == 404
    assert db.scalar(select(Document).where(Document.filename == "Blocked")) is None


def test_get_document_hides_other_users_document(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db)

    owned_response = client.get(f"/api/v1/documents/{records['document'].id}")
    other_response = client.get(f"/api/v1/documents/{records['other_document'].id}")

    assert owned_response.status_code == 200
    assert owned_response.json()["id"] == str(records["document"].id)
    assert other_response.status_code == 404


def test_delete_document_removes_related_chunks(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db)

    response = client.delete(f"/api/v1/documents/{records['document'].id}")
    document = db.scalar(select(Document).where(Document.id == records["document"].id))
    chunk = db.scalar(select(DocumentChunk).where(DocumentChunk.id == records["chunk"].id))

    assert response.status_code == 204
    assert document is None
    assert chunk is None


def test_list_documents_hides_other_users_project(db: Session) -> None:
    records = seed_documents(db)
    client = client_for(db, "auth-other")

    response = client.get(f"/api/v1/projects/{records['project'].id}/documents")

    assert response.status_code == 404
