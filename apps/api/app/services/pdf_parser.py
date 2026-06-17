from dataclasses import dataclass
from pathlib import Path

import fitz
from sqlalchemy.orm import Session

from app.models import Document
from app.services.chunking import replace_document_chunks

MIN_EXTRACTED_WORDS = 1


@dataclass(frozen=True)
class PdfParseResult:
    parse_status: str
    raw_text: str | None
    chunk_count: int
    error_message: str | None = None


def parse_pdf_document(db: Session, document: Document) -> PdfParseResult:
    if not document.storage_path:
        return _mark_failed(db, document, "PDF file is missing from storage.")

    try:
        raw_text = extract_pdf_text(Path(document.storage_path))
    except PdfParseError as exc:
        return _mark_failed(db, document, str(exc))

    if len(raw_text.split()) < MIN_EXTRACTED_WORDS:
        return _mark_failed(db, document, "No selectable text was found in this PDF.")

    document.raw_text = raw_text
    document.status = "parsed"
    document.parse_status = "parsed"
    chunks = replace_document_chunks(db, document.id, raw_text)
    return PdfParseResult(parse_status="parsed", raw_text=raw_text, chunk_count=len(chunks))


def extract_pdf_text(path: Path) -> str:
    try:
        with fitz.open(path) as pdf:
            page_text = [page.get_text("text").strip() for page in pdf]
    except Exception as exc:
        raise PdfParseError("This PDF could not be read. Try re-exporting it and uploading again.") from exc

    return "\n\n".join(text for text in page_text if text)


class PdfParseError(Exception):
    pass


def _mark_failed(db: Session, document: Document, error_message: str) -> PdfParseResult:
    document.status = "parse_failed"
    document.parse_status = "failed"
    document.raw_text = None
    replace_document_chunks(db, document.id, "")
    db.flush()
    return PdfParseResult(parse_status="failed", raw_text=None, chunk_count=0, error_message=error_message)
