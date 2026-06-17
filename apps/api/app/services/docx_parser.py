from dataclasses import dataclass
from pathlib import Path

from docx import Document as DocxDocument
from sqlalchemy.orm import Session

from app.models import Document
from app.services.chunking import replace_document_chunks

MIN_EXTRACTED_WORDS = 1


@dataclass(frozen=True)
class DocxParseResult:
    parse_status: str
    raw_text: str | None
    chunk_count: int
    error_message: str | None = None


def parse_docx_document(db: Session, document: Document) -> DocxParseResult:
    if not document.storage_path:
        return _mark_failed(db, document, "DOCX file is missing from storage.")

    try:
        raw_text = extract_docx_text(Path(document.storage_path))
    except DocxParseError as exc:
        return _mark_failed(db, document, str(exc))

    if len(raw_text.split()) < MIN_EXTRACTED_WORDS:
        return _mark_failed(db, document, "No text was found in this DOCX file.")

    document.raw_text = raw_text
    document.status = "parsed"
    document.parse_status = "parsed"
    chunks = replace_document_chunks(db, document.id, raw_text)
    return DocxParseResult(parse_status="parsed", raw_text=raw_text, chunk_count=len(chunks))


def extract_docx_text(path: Path) -> str:
    try:
        document = DocxDocument(path)
    except Exception as exc:
        raise DocxParseError("This DOCX file could not be read. Try re-exporting it and uploading again.") from exc

    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n\n".join(paragraphs)


class DocxParseError(Exception):
    pass


def _mark_failed(db: Session, document: Document, error_message: str) -> DocxParseResult:
    document.status = "parse_failed"
    document.parse_status = "failed"
    document.raw_text = None
    replace_document_chunks(db, document.id, "")
    db.flush()
    return DocxParseResult(parse_status="failed", raw_text=None, chunk_count=0, error_message=error_message)
