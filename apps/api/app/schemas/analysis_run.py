from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnalysisRunCreate(BaseModel):
    include_results_agent: bool = True


class AnalysisRunRead(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    summary: str | None
    overall_score: float | None
    current_agent: str | None
    progress_percentage: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisRunStatus(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    current_agent: str | None
    progress_percentage: int
    summary: str | None
    overall_score: float | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
