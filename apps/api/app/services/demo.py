import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.core.config import get_settings
from app.models import Document, Reference
from app.schemas.demo import DemoProjectRead
from app.schemas.document import DocumentTextCreate
from app.schemas.project import ProjectCreate
from app.services.bibtex_parser import parse_bibtex_document
from app.services.csv_parser import parse_csv_document
from app.services.documents import create_text_document
from app.services.projects import create_project


def find_demo_dir(source_file: Path = Path(__file__)) -> Path:
    for parent in source_file.resolve().parents:
        candidate = parent / "examples" / "demo-thesis"
        if candidate.is_dir():
            return candidate
    raise RuntimeError("Demo assets were not found in examples/demo-thesis.")


DEMO_DIR = find_demo_dir()


def load_demo_project(db: Session, current_user: AuthenticatedUser) -> DemoProjectRead:
    metadata = json.loads((DEMO_DIR / "project.json").read_text(encoding="utf-8"))
    thesis_text = (DEMO_DIR / "thesis_draft.txt").read_text(encoding="utf-8")

    project = create_project(db, current_user, ProjectCreate(**metadata))
    create_text_document(
        db,
        current_user,
        project.id,
        DocumentTextCreate(
            document_type="thesis_draft",
            title="Demo thesis draft",
            raw_text=thesis_text,
        ),
    )
    _create_parsed_demo_file(db, project.id, "reference_file", "references.bib", "text/plain", parse_bibtex_document)
    _create_parsed_demo_file(db, project.id, "results_file", "results.csv", "text/csv", parse_csv_document)

    document_count = db.scalar(select(func.count(Document.id)).where(Document.project_id == project.id)) or 0
    reference_count = db.scalar(select(func.count(Reference.id)).where(Reference.project_id == project.id)) or 0
    db.refresh(project)
    return DemoProjectRead(project=project, document_count=document_count, reference_count=reference_count)


def _create_parsed_demo_file(db: Session, project_id: UUID, document_type: str, filename: str, content_type: str, parser) -> Document:
    contents = (DEMO_DIR / filename).read_bytes()
    document = Document(
        project_id=project_id,
        filename=filename,
        content_type=content_type,
        document_type=document_type,
        size_bytes=len(contents),
        status="uploaded",
        parse_status="pending",
    )
    db.add(document)
    db.flush()

    storage_dir = Path(get_settings().upload_storage_dir) / str(project_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / f"{document.id}-{filename}"
    storage_path.write_bytes(contents)

    document.storage_path = str(storage_path)
    parser(db, document)
    db.commit()
    db.refresh(document)
    return document
