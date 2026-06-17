from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


TaskStatus = Literal["open", "in_progress", "completed", "dismissed"]


class ActionTaskUpdate(BaseModel):
    status: TaskStatus


class ActionTaskRead(BaseModel):
    id: UUID
    project_id: UUID
    report_id: UUID | None
    finding_id: UUID | None
    title: str
    description: str | None
    category: str | None
    priority: str
    status: str
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
