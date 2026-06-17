import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import AnalysisRun
from app.services.thesis_review_workflow import ThesisReviewWorkflow, WorkflowOptions

logger = logging.getLogger(__name__)


def run_analysis_workflow_job(
    analysis_run_id: str,
    *,
    include_results_agent: bool = True,
    use_band: bool = True,
) -> None:
    run_id = UUID(analysis_run_id)
    with SessionLocal() as db:
        try:
            ThesisReviewWorkflow().run(
                db,
                analysis_run_id=run_id,
                options=WorkflowOptions(include_results_agent=include_results_agent, use_band=use_band),
            )
        except Exception as exc:
            logger.exception("Analysis workflow job failed.", extra={"analysis_run_id": analysis_run_id})
            _mark_run_failed(db, run_id, str(exc) or "Analysis worker failed.")
            raise


def _mark_run_failed(db: Session, analysis_run_id: UUID, summary: str) -> None:
    analysis_run = db.get(AnalysisRun, analysis_run_id)
    if analysis_run is None:
        return
    analysis_run.status = "failed"
    analysis_run.summary = summary
    analysis_run.completed_at = datetime.now(UTC)
    db.commit()
