from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentTextCreate(BaseModel):
    document_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=255)
    raw_text: str


class DocumentRead(BaseModel):
    id: UUID
    project_id: UUID
    filename: str
    storage_path: str | None
    content_type: str | None
    document_type: str
    size_bytes: int | None
    status: str
    raw_text: str | None
    parse_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentTextRead(BaseModel):
    id: UUID
    project_id: UUID
    document_type: str
    title: str
    parse_status: str
    word_count: int
    chunk_count: int
