from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import AnalysisRun, Report, ThesisProject, UserProfile


def make_db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


def test_list_and_get_owned_reports() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        client = client_for(db)
        project, report = seed_report(db)

        list_response = client.get(f"/api/v1/projects/{project.id}/reports")
        detail_response = client.get(f"/api/v1/reports/{report.id}")

        assert list_response.status_code == 200
        reports = list_response.json()
        assert [item["id"] for item in reports] == [str(report.id)]
        assert reports[0]["overall_score"] == 82.0
        assert reports[0]["score_breakdown"] == {"gap": 80, "citation": 75}
        assert reports[0]["executive_summary"] == "The thesis is close to defense-ready."
        assert reports[0]["content"] == "# Thesis Health Report"
        assert reports[0]["structured_report"] == {"priority_fixes": ["Add baseline"]}
        assert "created_at" in reports[0]

        assert detail_response.status_code == 200
        assert detail_response.json()["id"] == str(report.id)
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_report_routes_hide_other_users_reports() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
        other = UserProfile(auth_user_id="auth-other", email="other@example.com")
        db.add_all([owner, other])
        db.flush()
        other_project = ThesisProject(owner_id=other.id, title="Other project")
        db.add(other_project)
        db.flush()
        other_report = Report(project_id=other_project.id, title="Other report", status="ready")
        db.add(other_report)
        db.commit()
        db.refresh(other_project)
        db.refresh(other_report)

        client = client_for(db)

        assert client.get(f"/api/v1/projects/{other_project.id}/reports").status_code == 404
        assert client.get(f"/api/v1/reports/{other_report.id}").status_code == 404
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def client_for(db: Session, auth_user_id: str = "auth-owner") -> TestClient:
    app.dependency_overrides.clear()

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        auth_user_id=auth_user_id,
        email=f"{auth_user_id}@example.com",
    )
    return TestClient(app)


def seed_report(db: Session) -> tuple[ThesisProject, Report]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Owned project")
    run = AnalysisRun(project=project, status="completed")
    report = Report(
        project=project,
        analysis_run=run,
        title="Thesis Health Report",
        status="ready",
        overall_score=82,
        score_breakdown={"gap": 80, "citation": 75},
        executive_summary="The thesis is close to defense-ready.",
        content="# Thesis Health Report",
        structured_report={"priority_fixes": ["Add baseline"]},
    )
    db.add_all([owner, project, run, report])
    db.commit()
    db.refresh(project)
    db.refresh(report)
    return project, report
