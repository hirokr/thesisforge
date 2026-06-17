from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.core.config import get_settings
from app.models import AgentMessage, AnalysisRun, ThesisProject
from app.services.ownership import require_owned_analysis_run, require_owned_project, require_profile_for_auth_user
from app.workers.analysis_runs import run_analysis_workflow_job

WORKFLOW_AGENT_ORDER = [
    "literature-review",
    "research-gap",
    "citation",
    "methodology-consistency",
    "results-interpretation",
    "defense-preparation",
    "report-generator",
]

TERMINAL_STATUSES = {"completed", "failed", "partial"}


def create_analysis_run(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> AnalysisRun:
    project = require_owned_project(db, current_user, project_id)
    analysis_run = AnalysisRun(project_id=project.id, status="queued")
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)
    return analysis_run


def enqueue_analysis_run(
    analysis_run: AnalysisRun,
    *,
    include_results_agent: bool = True,
    use_band: bool = True,
) -> str:
    settings = get_settings()
    try:
        from redis import Redis
        from rq import Queue

        queue = Queue(settings.analysis_queue_name, connection=Redis.from_url(settings.redis_url))
        job = queue.enqueue(
            run_analysis_workflow_job,
            str(analysis_run.id),
            include_results_agent=include_results_agent,
            use_band=use_band,
            job_timeout=settings.analysis_job_timeout_seconds,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis worker queue is unavailable.",
        ) from exc
    return str(job.id)


def list_analysis_runs(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> list[AnalysisRun]:
    project = require_owned_project(db, current_user, project_id)
    return list(
        db.scalars(
            select(AnalysisRun)
            .where(AnalysisRun.project_id == project.id)
            .order_by(AnalysisRun.created_at.desc(), AnalysisRun.updated_at.desc())
        )
    )


def get_analysis_run(db: Session, current_user: AuthenticatedUser, analysis_run_id: UUID) -> AnalysisRun:
    return require_owned_analysis_run(db, current_user, analysis_run_id)


def get_analysis_run_status(db: Session, current_user: AuthenticatedUser, analysis_run_id: UUID) -> AnalysisRun:
    return require_owned_analysis_run(db, current_user, analysis_run_id)


def attach_run_progress(db: Session, analysis_run: AnalysisRun) -> AnalysisRun:
    current_agent, progress_percentage = calculate_run_progress(db, analysis_run)
    setattr(analysis_run, "current_agent", current_agent)
    setattr(analysis_run, "progress_percentage", progress_percentage)
    return analysis_run


def calculate_run_progress(db: Session, analysis_run: AnalysisRun) -> tuple[str | None, int]:
    if analysis_run.status == "queued":
        return None, 0
    if analysis_run.status in TERMINAL_STATUSES:
        return None, 100

    handoff_tasks = list(
        db.scalars(
            select(AgentMessage.task)
            .where(
                AgentMessage.analysis_run_id == analysis_run.id,
                AgentMessage.message_type == "handoff",
                AgentMessage.task.is_not(None),
            )
            .order_by(AgentMessage.created_at.asc())
        )
    )
    completed_agents = {_from_agent_from_handoff_task(task) for task in handoff_tasks}
    completed_agents.discard(None)

    progress_percentage = min(int(len(completed_agents) / len(WORKFLOW_AGENT_ORDER) * 100), 95)
    current_agent = _next_agent(completed_agents)
    return current_agent, progress_percentage


def list_all_owned_analysis_runs(db: Session, current_user: AuthenticatedUser) -> list[AnalysisRun]:
    profile = require_profile_for_auth_user(db, current_user)
    return list(
        db.scalars(
            select(AnalysisRun)
            .join(ThesisProject)
            .where(ThesisProject.owner_id == profile.id)
            .order_by(AnalysisRun.created_at.desc(), AnalysisRun.updated_at.desc())
        )
    )


def _from_agent_from_handoff_task(task: str | None) -> str | None:
    if not task or "_to_" not in task:
        return None
    return task.split("_to_", 1)[0]


def _next_agent(completed_agents: set[str | None]) -> str | None:
    for slug in WORKFLOW_AGENT_ORDER:
        if slug not in completed_agents:
            return slug
    return None
