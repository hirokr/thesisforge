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


class AgentMessageRead(BaseModel):
    id: UUID
    analysis_run_id: UUID
    project_id: UUID | None
    from_agent_id: UUID | None
    from_agent_name: str | None
    from_agent_slug: str | None
    to_agent_id: UUID | None
    to_agent_name: str | None
    to_agent_slug: str | None
    message_type: str
    task: str | None
    summary: str | None
    content: str
    status: str
    band_message_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
