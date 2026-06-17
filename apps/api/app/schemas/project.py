from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    research_area: str | None = Field(default=None, max_length=255)
    thesis_stage: str | None = Field(default=None, max_length=100)
    problem_statement: str | None = None
    research_gap: str | None = None
    objectives: str | None = None
    methodology_summary: str | None = None
    dataset_summary: str | None = None
    results_summary: str | None = None
    abstract: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    research_area: str | None = Field(default=None, max_length=255)
    thesis_stage: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=50)
    problem_statement: str | None = None
    research_gap: str | None = None
    objectives: str | None = None
    methodology_summary: str | None = None
    dataset_summary: str | None = None
    results_summary: str | None = None
    abstract: str | None = None

    model_config = ConfigDict(extra="forbid")


class ProjectRead(ProjectBase):
    id: UUID
    owner_id: UUID
    status: str
    latest_score: float | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
