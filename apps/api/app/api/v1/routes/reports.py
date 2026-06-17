from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.schemas.report import ReportRead
from app.services.reports import get_report, list_project_reports

router = APIRouter(tags=["reports"])


@router.get("/projects/{project_id}/reports", response_model=list[ReportRead])
def list_project_reports_route(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReportRead]:
    return list_project_reports(db, current_user, project_id)


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report_route(
    report_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportRead:
    return get_report(db, current_user, report_id)
