from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import UserProfile


def build_client(db: Session, current_user: AuthenticatedUser) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app)


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_me_returns_existing_profile() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as db:
        profile = UserProfile(
            auth_user_id="auth-existing",
            email="researcher@example.com",
            full_name="Existing Researcher",
            role="researcher",
            institution="ThesisForge University",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        client = build_client(db, AuthenticatedUser(auth_user_id="auth-existing", email="ignored@example.com"))
        response = client.get("/api/v1/me")

    clear_overrides()

    assert response.status_code == 200
    assert response.json() == {
        "id": str(profile.id),
        "auth_user_id": "auth-existing",
        "email": "researcher@example.com",
        "full_name": "Existing Researcher",
        "role": "researcher",
        "institution": "ThesisForge University",
    }


def test_me_creates_missing_profile_without_privilege_escalation() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    current_user = AuthenticatedUser(
        auth_user_id="auth-new",
        email="new@example.com",
        claims={"user_metadata": {"full_name": "New Researcher", "role": "admin"}},
    )

    with TestingSessionLocal() as db:
        client = build_client(db, current_user)
        response = client.get("/api/v1/me")
        profile = db.scalar(select(UserProfile).where(UserProfile.auth_user_id == "auth-new"))

    clear_overrides()

    assert response.status_code == 200
    assert response.json()["auth_user_id"] == "auth-new"
    assert response.json()["email"] == "new@example.com"
    assert response.json()["full_name"] == "New Researcher"
    assert response.json()["role"] == "researcher"
    assert profile is not None
    assert profile.role == "researcher"
