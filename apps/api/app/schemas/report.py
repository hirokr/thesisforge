from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportRead(BaseModel):
    id: UUID
    project_id: UUID
    analysis_run_id: UUID | None
    title: str
    status: str
    overall_score: float | None
    score_breakdown: dict | None
    executive_summary: str | None
    content: str | None
    structured_report: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
