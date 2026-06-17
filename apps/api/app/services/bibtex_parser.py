from dataclasses import dataclass
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import Document, Reference


@dataclass(frozen=True)
class BibTeXParseResult:
    parse_status: str
    reference_count: int
    error_message: str | None = None


def parse_bibtex_document(db: Session, document: Document) -> BibTeXParseResult:
    if not document.storage_path:
        return _mark_failed(db, document, "BibTeX file is missing from storage.")

    try:
        raw_text = Path(document.storage_path).read_text(encoding="utf-8")
        entries = parse_bibtex_entries(raw_text)
    except BibTeXParseError as exc:
        return _mark_failed(db, document, str(exc))
    except UnicodeDecodeError:
        return _mark_failed(db, document, "This BibTeX file must be UTF-8 encoded.")

    if not entries:
        return _mark_failed(db, document, "No valid BibTeX references were found.")

    db.execute(delete(Reference).where(Reference.document_id == document.id))
    references = [
        Reference(
            project_id=document.project_id,
            document_id=document.id,
            citation_key=entry.citation_key,
            title=entry.title,
            authors=entry.authors,
            year=entry.year,
            venue=entry.venue,
            doi=entry.doi,
            url=entry.url,
            citation_text=entry.citation_text,
            raw_bibtex=entry.raw_bibtex,
        )
        for entry in entries
    ]
    db.add_all(references)
    document.raw_text = raw_text
    document.status = "parsed"
    document.parse_status = "parsed"
    return BibTeXParseResult(parse_status="parsed", reference_count=len(references))


@dataclass(frozen=True)
class ParsedBibTeXEntry:
    citation_key: str | None
    title: str | None
    authors: list[str] | None
    year: int | None
    venue: str | None
    doi: str | None
    url: str | None
    citation_text: str | None
    raw_bibtex: str


def parse_bibtex_entries(raw_text: str) -> list[ParsedBibTeXEntry]:
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False

    try:
        library = bibtexparser.loads(raw_text, parser=parser)
    except Exception as exc:
        raise BibTeXParseError("This BibTeX file could not be parsed.") from exc

    entries: list[ParsedBibTeXEntry] = []
    for entry in library.entries:
        citation_key = _clean(entry.get("ID"))
        if not citation_key:
            continue

        title = _clean(entry.get("title"))
        venue = _clean(entry.get("journal") or entry.get("booktitle") or entry.get("publisher"))
        parsed = ParsedBibTeXEntry(
            citation_key=citation_key,
            title=title,
            authors=_parse_authors(entry.get("author")),
            year=_parse_year(entry.get("year")),
            venue=venue,
            doi=_clean(entry.get("doi")),
            url=_clean(entry.get("url")),
            citation_text=_build_citation_text(citation_key, title, entry.get("author"), entry.get("year"), venue),
            raw_bibtex=_render_raw_entry(entry),
        )
        entries.append(parsed)

    return entries


class BibTeXParseError(Exception):
    pass


def _mark_failed(db: Session, document: Document, error_message: str) -> BibTeXParseResult:
    db.execute(delete(Reference).where(Reference.document_id == document.id))
    document.status = "parse_failed"
    document.parse_status = "failed"
    document.raw_text = None
    db.flush()
    return BibTeXParseResult(parse_status="failed", reference_count=0, error_message=error_message)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.replace("{", "").replace("}", "").split())
    return cleaned or None


def _parse_authors(value: str | None) -> list[str] | None:
    if not value:
        return None
    authors = [_clean(author) for author in value.split(" and ")]
    normalized = [author for author in authors if author]
    return normalized or None


def _parse_year(value: str | None) -> int | None:
    if not value:
        return None
    year_digits = "".join(character for character in value if character.isdigit())
    if len(year_digits) < 4:
        return None
    return int(year_digits[:4])


def _build_citation_text(
    citation_key: str,
    title: str | None,
    author: str | None,
    year: str | None,
    venue: str | None,
) -> str:
    parts = [_clean(author), _clean(year), title, venue]
    citation_body = ". ".join(part for part in parts if part)
    return f"{citation_key}: {citation_body}" if citation_body else citation_key


def _render_raw_entry(entry: dict[str, str]) -> str:
    entry_type = entry.get("ENTRYTYPE", "misc")
    citation_key = entry.get("ID", "unknown")
    fields = [
        f"  {key} = {{{value}}}"
        for key, value in sorted(entry.items())
        if key not in {"ENTRYTYPE", "ID"}
    ]
    return "@{entry_type}{{{citation_key},\n{fields}\n}}".format(
        entry_type=entry_type,
        citation_key=citation_key,
        fields=",\n".join(fields),
    )
