from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import Report
from app.services.analytics import log_analytics_event
from app.services.ownership import require_owned_project, require_owned_report
from app.services.user_profiles import get_or_create_user_profile


def list_project_reports(db: Session, current_user: AuthenticatedUser, project_id: UUID) -> list[Report]:
    project = require_owned_project(db, current_user, project_id)
    return list(
        db.scalars(
            select(Report)
            .where(Report.project_id == project.id)
            .order_by(Report.created_at.desc(), Report.updated_at.desc())
        )
    )


def get_report(db: Session, current_user: AuthenticatedUser, report_id: UUID) -> Report:
    report = require_owned_report(db, current_user, report_id)
    profile = get_or_create_user_profile(db, current_user)
    log_report_event(db, profile.id, report, "report_viewed")
    db.commit()
    db.refresh(report)
    return report


def track_report_event(db: Session, current_user: AuthenticatedUser, report_id: UUID, event_name: str) -> Report:
    report = require_owned_report(db, current_user, report_id)
    profile = get_or_create_user_profile(db, current_user)
    log_report_event(db, profile.id, report, event_name)
    db.commit()
    db.refresh(report)
    return report


def log_report_event(db: Session, actor_user_id: UUID, report: Report, event_name: str) -> None:
    log_analytics_event(
        db,
        event_name=event_name,
        project_id=report.project_id,
        actor_user_id=actor_user_id,
        entity_type="report",
        entity_id=report.id,
        details={
            "analysis_run_id": str(report.analysis_run_id) if report.analysis_run_id else None,
            "status": report.status,
            "overall_score": report.overall_score,
        },
    )
