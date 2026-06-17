from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError
from sqlalchemy.orm import Session

from app.models import Document

SAMPLE_ROW_LIMIT = 5


@dataclass(frozen=True)
class CsvParseResult:
    parse_status: str
    parse_metadata: dict | None
    error_message: str | None = None


def parse_csv_document(db: Session, document: Document) -> CsvParseResult:
    if not document.storage_path:
        return _mark_failed(db, document, "CSV file is missing from storage.")

    try:
        summary = summarize_csv(Path(document.storage_path))
    except CsvParseError as exc:
        return _mark_failed(db, document, str(exc))

    document.status = "parsed"
    document.parse_status = "parsed"
    document.parse_metadata = summary
    document.raw_text = None
    return CsvParseResult(parse_status="parsed", parse_metadata=summary)


def summarize_csv(path: Path) -> dict:
    try:
        frame = pd.read_csv(path, on_bad_lines="error")
    except EmptyDataError as exc:
        raise CsvParseError("No CSV columns were found in this file.") from exc
    except (ParserError, UnicodeDecodeError) as exc:
        raise CsvParseError("This CSV file could not be parsed. Check the delimiter and row formatting.") from exc

    sample = frame.head(SAMPLE_ROW_LIMIT).where(pd.notna(frame.head(SAMPLE_ROW_LIMIT)), None)
    return {
        "row_count": int(len(frame)),
        "column_names": [str(column) for column in frame.columns],
        "sample_rows": sample.to_dict(orient="records"),
    }


class CsvParseError(Exception):
    pass


def _mark_failed(db: Session, document: Document, error_message: str) -> CsvParseResult:
    document.status = "parse_failed"
    document.parse_status = "failed"
    document.parse_metadata = None
    document.raw_text = None
    db.flush()
    return CsvParseResult(parse_status="failed", parse_metadata=None, error_message=error_message)
