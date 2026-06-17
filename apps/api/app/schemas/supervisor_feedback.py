from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


FeedbackSource = Literal["meeting", "email", "document_comment", "manual"]


class SupervisorFeedbackCreate(BaseModel):
    feedback_text: str = Field(min_length=1)
    source: FeedbackSource = "manual"
    feedback_date: datetime | None = None


class SupervisorFeedbackRead(BaseModel):
    id: UUID
    project_id: UUID
    feedback_text: str
    source: str
    feedback_date: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
