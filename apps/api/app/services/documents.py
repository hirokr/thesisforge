from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import Document
from app.services.ownership import require_owned_document, require_owned_project


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


def delete_document(db: Session, current_user: AuthenticatedUser, document_id: UUID) -> None:
    document = require_owned_document(db, current_user, document_id)
    db.delete(document)
    db.commit()
