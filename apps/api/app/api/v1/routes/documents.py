from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.rate_limit import file_upload_rate_limit
from app.db.session import get_db
from app.schemas.document import DocumentRead, DocumentTextCreate, DocumentTextRead
from app.services.documents import (
    create_text_document,
    create_uploaded_document,
    delete_document,
    get_document,
    list_project_documents,
)

router = APIRouter(tags=["documents"])


@router.get("/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_project_documents_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentRead]:
    return list_project_documents(db, current_user, project_id)


@router.post(
    "/projects/{project_id}/documents/text",
    response_model=DocumentTextRead,
    status_code=status.HTTP_201_CREATED,
)
def create_text_document_route(
    project_id: UUID,
    payload: DocumentTextCreate,
    _rate_limit: None = Depends(file_upload_rate_limit),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentTextRead:
    document, word_count, chunk_count = create_text_document(db, current_user, project_id, payload)
    return DocumentTextRead(
        id=document.id,
        project_id=document.project_id,
        document_type=document.document_type,
        title=document.filename,
        parse_status=document.parse_status,
        word_count=word_count,
        chunk_count=chunk_count,
    )


@router.post("/projects/{project_id}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document_route(
    project_id: UUID,
    document_type: str = Form(..., min_length=1, max_length=80),
    file: UploadFile = File(...),
    _rate_limit: None = Depends(file_upload_rate_limit),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentRead:
    return create_uploaded_document(db, current_user, project_id, document_type, file)


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
