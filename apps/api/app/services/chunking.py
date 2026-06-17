from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import DocumentChunk

DEFAULT_MAX_CHUNK_WORDS = 350
MAX_HEADING_WORDS = 12


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    content: str


def count_words(text: str) -> int:
    return len(text.split())


def chunk_text(text: str, max_words: int = DEFAULT_MAX_CHUNK_WORDS) -> list[TextChunk]:
    if max_words < 1:
        raise ValueError("max_words must be greater than zero")

    paragraphs = [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current_parts: list[str] = []
    current_word_count = 0
    active_heading: str | None = None

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        paragraph_word_count = len(paragraph_words)

        if _looks_like_heading(paragraph):
            if current_parts and current_word_count + paragraph_word_count > max_words:
                chunks.append("\n\n".join(current_parts))
                current_parts = []
                current_word_count = 0
            active_heading = paragraph
            current_parts.append(paragraph)
            current_word_count = paragraph_word_count
            continue

        if paragraph_word_count > max_words:
            if current_parts and current_parts != [active_heading]:
                chunks.append("\n\n".join(current_parts))
            current_parts = []
            current_word_count = 0
            chunks.extend(_split_long_paragraph(paragraph_words, max_words, active_heading))
            continue

        if current_parts and current_word_count + paragraph_word_count > max_words:
            chunks.append("\n\n".join(current_parts))
            current_parts = [active_heading] if active_heading else []
            current_word_count = count_words(active_heading) if active_heading else 0

        current_parts.append(paragraph)
        current_word_count += paragraph_word_count

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return [TextChunk(chunk_index=index, content=content) for index, content in enumerate(chunks)]


def replace_document_chunks(db: Session, document_id: UUID, text: str, max_words: int = DEFAULT_MAX_CHUNK_WORDS) -> list[DocumentChunk]:
    chunks = chunk_text(text, max_words=max_words)
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

    records = [
        DocumentChunk(document_id=document_id, chunk_index=chunk.chunk_index, content=chunk.content)
        for chunk in chunks
    ]
    db.add_all(records)
    return records


def _looks_like_heading(paragraph: str) -> bool:
    words = paragraph.split()
    if not words or len(words) > MAX_HEADING_WORDS:
        return False

    if paragraph.endswith((".", ",", ";", ":")):
        return False

    first_word = words[0].strip("0123456789.()[]").lower()
    known_headings = {
        "abstract",
        "background",
        "conclusion",
        "discussion",
        "evaluation",
        "experiment",
        "experiments",
        "introduction",
        "method",
        "methodology",
        "results",
        "references",
        "related",
    }
    return first_word in known_headings or paragraph.isupper() or paragraph.istitle()


def _split_long_paragraph(words: list[str], max_words: int, heading: str | None) -> list[str]:
    chunks: list[str] = []
    heading_words = count_words(heading) if heading else 0
    body_word_limit = max_words - heading_words if heading and heading_words < max_words else max_words

    for index in range(0, len(words), body_word_limit):
        body = " ".join(words[index : index + body_word_limit])
        chunks.append(f"{heading}\n\n{body}" if heading else body)

    return chunks
