import re
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.core.config import get_settings
from app.models import Document
from app.schemas.document import DocumentTextCreate
from app.services.bibtex_parser import parse_bibtex_document
from app.services.chunking import count_words, replace_document_chunks
from app.services.csv_parser import parse_csv_document
from app.services.docx_parser import parse_docx_document
from app.services.ownership import require_owned_document, require_owned_project
from app.services.pdf_parser import parse_pdf_document

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
SUPPORTED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".txt", ".bib", ".csv"}
UPLOAD_CONTENT_TYPES: dict[str, set[str]] = {
    ".bib": {"text/plain", "application/x-bibtex", "text/x-bibtex"},
    ".csv": {"text/csv", "application/csv", "application/vnd.ms-excel"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".pdf": {"application/pdf"},
    ".txt": {"text/plain"},
}
DEFAULT_CONTENT_TYPES = {
    extension: sorted(content_types)[0] for extension, content_types in UPLOAD_CONTENT_TYPES.items()
}


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

    chunks = replace_document_chunks(db, document.id, payload.raw_text)

    db.commit()
    db.refresh(document)
    return document, word_count, len(chunks)


def create_uploaded_document(
    db: Session,
    current_user: AuthenticatedUser,
    project_id: UUID,
    document_type: str,
    upload: UploadFile,
) -> Document:
    project = require_owned_project(db, current_user, project_id)
    safe_filename, extension, content_type = _validate_upload_metadata(upload)
    contents = upload.file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Files must be 25 MB or smaller.")
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded files cannot be empty.")

    document = Document(
        project_id=project.id,
        filename=safe_filename,
        content_type=content_type,
        document_type=document_type,
        size_bytes=len(contents),
        status="uploaded",
        parse_status="pending",
    )
    db.add(document)
    db.flush()

    storage_root = Path(get_settings().upload_storage_dir)
    project_dir = storage_root / str(project.id)
    project_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{document.id}-{safe_filename}"
    storage_path = project_dir / stored_filename
    storage_path.write_bytes(contents)

    document.storage_path = str(storage_path)
    if extension == ".pdf":
        parse_pdf_document(db, document)
    elif extension == ".docx":
        parse_docx_document(db, document)
    elif extension == ".bib":
        parse_bibtex_document(db, document)
    elif extension == ".csv":
        parse_csv_document(db, document)

    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, current_user: AuthenticatedUser, document_id: UUID) -> None:
    document = require_owned_document(db, current_user, document_id)
    db.delete(document)
    db.commit()


def _safe_filename(filename: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(filename).name).strip(".-")
    return safe or "upload"


def _validate_upload_metadata(upload: UploadFile) -> tuple[str, str, str]:
    original_filename = Path(upload.filename or "").name
    extension = Path(original_filename).suffix.lower()
    if not original_filename or extension not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Upload PDF, DOCX, TXT, BIB, or CSV files only.",
        )

    content_type = _normalize_content_type(upload.content_type)
    if content_type not in UPLOAD_CONTENT_TYPES[extension]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content type does not match the allowed type for this extension.",
        )

    safe_filename = _safe_filename(original_filename)
    if Path(safe_filename).suffix.lower() != extension:
        safe_filename = f"{safe_filename}{extension}"

    return safe_filename, extension, content_type or DEFAULT_CONTENT_TYPES[extension]


def _normalize_content_type(content_type: str | None) -> str:
    return (content_type or "").split(";", 1)[0].strip().lower()
