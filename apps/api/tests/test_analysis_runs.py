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
from app.models import AgentMessage, AnalysisRun, ThesisProject, UserProfile
from app.workers.analysis_runs import run_analysis_workflow_job


def make_db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


def test_create_list_get_and_poll_analysis_run(monkeypatch) -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        enqueued_runs: list[str] = []
        monkeypatch.setattr(
            "app.api.v1.routes.analysis_runs.enqueue_analysis_run",
            lambda analysis_run, **kwargs: enqueued_runs.append(str(analysis_run.id)) or "job-id",
        )
        client = client_for(db)
        project = seed_project(db)

        create_response = client.post(f"/api/v1/projects/{project.id}/analysis-runs")
        list_response = client.get(f"/api/v1/projects/{project.id}/analysis-runs")
        created = create_response.json()
        detail_response = client.get(f"/api/v1/analysis-runs/{created['id']}")
        status_response = client.get(f"/api/v1/analysis-runs/{created['id']}/status")

        assert create_response.status_code == 201
        assert created["project_id"] == str(project.id)
        assert created["status"] == "queued"
        assert created["current_agent"] is None
        assert created["progress_percentage"] == 0
        assert enqueued_runs == [created["id"]]
        assert list_response.status_code == 200
        assert [run["id"] for run in list_response.json()] == [created["id"]]
        assert detail_response.status_code == 200
        assert detail_response.json()["id"] == created["id"]
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "queued"

        saved_run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == UUID(created["id"])))
        assert saved_run is not None
        assert saved_run.project_id == project.id
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_analysis_run_routes_hide_other_users_runs() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
        other = UserProfile(auth_user_id="auth-other", email="other@example.com")
        db.add_all([owner, other])
        db.flush()
        project = ThesisProject(owner_id=owner.id, title="Owned project")
        other_project = ThesisProject(owner_id=other.id, title="Other project")
        db.add_all([project, other_project])
        db.flush()
        other_run = AnalysisRun(project_id=other_project.id, status="queued")
        db.add(other_run)
        db.commit()
        db.refresh(project)
        db.refresh(other_project)
        db.refresh(other_run)

        client = client_for(db)

        assert client.post(f"/api/v1/projects/{other_project.id}/analysis-runs").status_code == 404
        assert client.get(f"/api/v1/projects/{other_project.id}/analysis-runs").status_code == 404
        assert client.get(f"/api/v1/analysis-runs/{other_run.id}").status_code == 404
        assert client.get(f"/api/v1/analysis-runs/{other_run.id}/status").status_code == 404
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_running_analysis_run_status_reports_progress_from_handoffs() -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        client = client_for(db)
        project = seed_project(db)
        run = AnalysisRun(project_id=project.id, status="running")
        db.add(run)
        db.flush()
        db.add(
            AgentMessage(
                analysis_run_id=run.id,
                project_id=project.id,
                role="assistant",
                content="Literature handoff complete.",
                message_type="handoff",
                task="literature-review_to_research-gap",
                summary="Literature review complete.",
                status="sent",
            )
        )
        db.commit()
        db.refresh(run)

        response = client.get(f"/api/v1/analysis-runs/{run.id}/status")

        assert response.status_code == 200
        assert response.json()["status"] == "running"
        assert response.json()["current_agent"] == "research-gap"
        assert response.json()["progress_percentage"] == 14
    finally:
        app.dependency_overrides.clear()
        next(db_generator, None)


def test_worker_failure_marks_analysis_run_failed(monkeypatch) -> None:
    db_generator = make_db()
    db = next(db_generator)
    try:
        project = seed_project(db)
        run = AnalysisRun(project_id=project.id, status="queued")
        db.add(run)
        db.commit()
        db.refresh(run)

        class FailingWorkflow:
            def run(self, *args, **kwargs):
                raise RuntimeError("workflow crashed")

        class NoCloseSession:
            def __enter__(self) -> Session:
                return db

            def __exit__(self, *args) -> None:
                return None

        monkeypatch.setattr("app.workers.analysis_runs.SessionLocal", lambda: NoCloseSession())
        monkeypatch.setattr("app.workers.analysis_runs.ThesisReviewWorkflow", lambda: FailingWorkflow())

        try:
            run_analysis_workflow_job(str(run.id))
        except RuntimeError:
            pass

        db.refresh(run)
        assert run.status == "failed"
        assert run.summary == "workflow crashed"
        assert run.completed_at is not None
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


def seed_project(db: Session) -> ThesisProject:
    owner = UserProfile(auth_user_id="auth-owner", email="owner@example.com")
    project = ThesisProject(owner=owner, title="Owned project")
    db.add_all([owner, project])
    db.commit()
    db.refresh(project)
    return project
