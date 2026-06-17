from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser
from app.models import Report
from app.services.ownership import require_owned_project, require_owned_report


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
    return require_owned_report(db, current_user, report_id)
