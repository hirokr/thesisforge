from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.models import AgentMessage
from app.schemas.analysis_run import AgentMessageRead, AnalysisRunCreate, AnalysisRunRead, AnalysisRunStatus
from app.services.analysis_runs import (
    attach_run_progress,
    create_analysis_run,
    enqueue_analysis_run,
    get_analysis_run,
    get_analysis_run_status,
    list_agent_messages,
    list_analysis_runs,
)

router = APIRouter(tags=["analysis-runs"])


@router.post("/projects/{project_id}/analysis-runs", response_model=AnalysisRunRead, status_code=status.HTTP_201_CREATED)
def create_analysis_run_route(
    project_id: UUID,
    payload: AnalysisRunCreate | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisRunRead:
    options = payload or AnalysisRunCreate()
    analysis_run = create_analysis_run(db, current_user, project_id)
    enqueue_analysis_run(analysis_run, include_results_agent=options.include_results_agent)
    return attach_run_progress(db, analysis_run)


@router.get("/projects/{project_id}/analysis-runs", response_model=list[AnalysisRunRead])
def list_analysis_runs_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisRunRead]:
    return [attach_run_progress(db, analysis_run) for analysis_run in list_analysis_runs(db, current_user, project_id)]


@router.get("/analysis-runs/{run_id}", response_model=AnalysisRunRead)
def get_analysis_run_route(
    run_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisRunRead:
    return attach_run_progress(db, get_analysis_run(db, current_user, run_id))


@router.get("/analysis-runs/{run_id}/status", response_model=AnalysisRunStatus)
def get_analysis_run_status_route(
    run_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisRunStatus:
    return attach_run_progress(db, get_analysis_run_status(db, current_user, run_id))


@router.get("/analysis-runs/{run_id}/agent-messages", response_model=list[AgentMessageRead])
def list_agent_messages_route(
    run_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AgentMessageRead]:
    return [_serialize_agent_message(message) for message in list_agent_messages(db, current_user, run_id)]


def _serialize_agent_message(message: AgentMessage) -> AgentMessageRead:
    return AgentMessageRead(
        id=message.id,
        analysis_run_id=message.analysis_run_id,
        project_id=message.project_id,
        from_agent_id=message.from_agent_id,
        from_agent_name=message.from_agent.name if message.from_agent else None,
        from_agent_slug=message.from_agent.slug if message.from_agent else None,
        to_agent_id=message.to_agent_id,
        to_agent_name=message.to_agent.name if message.to_agent else None,
        to_agent_slug=message.to_agent.slug if message.to_agent else None,
        message_type=message.message_type,
        task=message.task,
        summary=message.summary,
        content=message.content,
        status=message.status,
        band_message_id=message.band_message_id,
        created_at=message.created_at,
    )
