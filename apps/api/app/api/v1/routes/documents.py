from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.document import DocumentRead
from app.services.documents import delete_document, get_document, list_project_documents

router = APIRouter(tags=["documents"])


@router.get("/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_project_documents_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentRead]:
    return list_project_documents(db, current_user, project_id)


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_route(
    document_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentRead:
    return get_document(db, current_user, document_id)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_route(
    document_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    delete_document(db, current_user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
