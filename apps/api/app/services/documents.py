from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import Document, DocumentChunk
from app.schemas.document import DocumentTextCreate
from app.services.ownership import require_owned_document, require_owned_project

MAX_CHUNK_WORDS = 350


def list_project_documents(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> list[Document]:
    project = require_owned_project(db, current_user, project_id)
    return list(
        db.scalars(
            select(Document)
            .where(Document.project_id == project.id)
            .order_by(Document.created_at.desc(), Document.filename.asc())
        )
    )


def get_document(db: Session, current_user: AuthenticatedUser, document_id: UUID) -> Document:
    return require_owned_document(db, current_user, document_id)


def create_text_document(
    db: Session,
    current_user: AuthenticatedUser,
    project_id: UUID,
    payload: DocumentTextCreate,
) -> tuple[Document, int, int]:
    project = require_owned_project(db, current_user, project_id)
    word_count = count_words(payload.raw_text)
    chunks = split_text_into_chunks(payload.raw_text)
    document = Document(
        project_id=project.id,
        filename=payload.title,
        content_type="text/plain",
        document_type=payload.document_type,
        size_bytes=len(payload.raw_text.encode("utf-8")),
        status="parsed",
        raw_text=payload.raw_text,
        parse_status="parsed",
    )
    db.add(document)
    db.flush()

    for chunk_index, chunk_content in enumerate(chunks):
        db.add(DocumentChunk(document_id=document.id, chunk_index=chunk_index, content=chunk_content))

    db.commit()
    db.refresh(document)
    return document, word_count, len(chunks)


def delete_document(db: Session, current_user: AuthenticatedUser, document_id: UUID) -> None:
    document = require_owned_document(db, current_user, document_id)
    db.delete(document)
    db.commit()


def count_words(text: str) -> int:
    return len(text.split())


def split_text_into_chunks(text: str, max_words: int = MAX_CHUNK_WORDS) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]
    chunks: list[str] = []
    current_words: list[str] = []

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        if len(paragraph_words) > max_words:
            if current_words:
                chunks.append(" ".join(current_words))
                current_words = []
            chunks.extend(_split_words(paragraph_words, max_words))
            continue

        if current_words and len(current_words) + len(paragraph_words) > max_words:
            chunks.append(" ".join(current_words))
            current_words = []

        current_words.extend(paragraph_words)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def _split_words(words: list[str], max_words: int) -> list[str]:
    return [" ".join(words[index : index + max_words]) for index in range(0, len(words), max_words)]
