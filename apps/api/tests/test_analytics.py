from collections.abc import Generator
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import AnalysisRun, AuditLog, Report, ThesisProject, UserProfile
from app.services.thesis_review_workflow import ThesisReviewWorkflow


def make_db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


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


def test_project_document_and_analysis_events_store_safe_metadata(monkeypatch) -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        enqueued_runs: list[str] = []
        monkeypatch.setattr(
            "app.api.v1.routes.analysis_runs.enqueue_analysis_run",
            lambda analysis_run, **kwargs: enqueued_runs.append(str(analysis_run.id)) or "job-id",
        )
        client = client_for(db)

        project_response = client.post(
            "/api/v1/projects",
            json={"title": "Private Thesis Title", "thesis_stage": "draft", "problem_statement": "Secret thesis content"},
        )
        project_id = project_response.json()["id"]
        document_response = client.post(
            f"/api/v1/projects/{project_id}/documents/text",
            json={
                "document_type": "thesis_draft",
                "title": "draft.txt",
                "raw_text": "Confidential thesis claim. " * 12,
            },
        )
        run_response = client.post(f"/api/v1/projects/{project_id}/analysis-runs")

        assert project_response.status_code == 201
        assert document_response.status_code == 201
        assert run_response.status_code == 201
        assert enqueued_runs == [run_response.json()["id"]]

        events = analytics_events(db)
        assert {event.action for event in events} == {"project_created", "document_uploaded", "analysis_started"}
        assert event_by_action(events, "project_created").entity_type == "project"
        document_event = event_by_action(events, "document_uploaded")
        assert document_event.entity_type == "document"
        assert document_event.details == {
            "document_type": "thesis_draft",
            "content_type": "text/plain",
            "parse_status": "parsed",
            "source": "pasted_text",
            "size_bytes": 324,
            "chunk_count": 1,
            "word_count": 36,
        }
        assert "Private Thesis Title" not in str([event.details for event in events])
        assert "Confidential thesis claim" not in str([event.details for event in events])
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_analysis_completed_event_is_logged_without_findings() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
        db.add(owner)
        db.flush()
        project = ThesisProject(owner_id=owner.id, title="Analytics project")
        db.add(project)
        db.flush()
        run = AnalysisRun(project_id=project.id, status="running", overall_score=88)
        db.add(run)
        db.commit()
        db.refresh(run)

        ThesisReviewWorkflow()._mark_completed(db, run)

        event = db.scalar(select(AuditLog).where(AuditLog.action == "analysis_completed"))
        assert event is not None
        assert event.project_id == project.id
        assert event.actor_user_id == owner.id
        assert event.entity_id == run.id
        assert event.details == {"status": "completed", "overall_score": 88}
    finally:
        next(db_generator, None)


def test_report_viewed_and_copied_events_are_report_scoped() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        client = client_for(db)
        project, report = seed_report(db)

        view_response = client.get(f"/api/v1/reports/{report.id}")
        copy_response = client.post(f"/api/v1/reports/{report.id}/events", json={"event_name": "report_copied"})
        invalid_response = client.post(f"/api/v1/reports/{report.id}/events", json={"event_name": "project_created"})

        assert view_response.status_code == 200
        assert copy_response.status_code == 204
        assert invalid_response.status_code == 422

        events = analytics_events(db)
        assert {event.action for event in events} == {"report_viewed", "report_copied"}
        assert all(event.project_id == project.id for event in events)
        assert all(event.entity_type == "report" for event in events)
        assert all(event.entity_id == report.id for event in events)
        assert "Full private markdown report" not in str([event.details for event in events])
        assert event_by_action(events, "report_viewed").details == {"analysis_run_id": None, "status": "completed", "overall_score": 82}
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def seed_report(db: Session) -> tuple[ThesisProject, Report]:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    db.add(owner)
    db.flush()
    project = ThesisProject(owner_id=owner.id, title="Owned project")
    db.add(project)
    db.flush()
    report = Report(
        project_id=project.id,
        title="Thesis Health Report",
        status="completed",
        overall_score=82,
        content="Full private markdown report",
    )
    db.add(report)
    db.commit()
    db.refresh(project)
    db.refresh(report)
    return project, report


def analytics_events(db: Session) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog)))


def event_by_action(events: list[AuditLog], action: str) -> AuditLog:
    for event in events:
        if event.action == action:
            return event
    raise AssertionError(f"Missing analytics event: {action}")
