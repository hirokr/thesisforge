from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.config import Settings, get_settings
from app.core.errors import install_error_handlers

TEST_SECRET = "test-supabase-jwt-secret"


def create_test_app() -> FastAPI:
    app = FastAPI()
    install_error_handlers(app)
    app.dependency_overrides[get_settings] = lambda: Settings(supabase_jwt_secret=TEST_SECRET)

    @app.get("/protected")
    async def protected_route(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict[str, str | None]:
        return {"auth_user_id": current_user.auth_user_id, "email": current_user.email}

    return app


def make_token(**claims: object) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "7bdb3f6b-9c01-421a-9d7a-3d1777bbf670",
        "aud": "authenticated",
        "email": "researcher@example.com",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        **claims,
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


def test_protected_route_rejects_missing_token() -> None:
    client = TestClient(create_test_app())

    response = client.get("/protected")

    assert response.status_code == 401
    body = response.json()
    assert body["error"] is True
    assert body["code"] == "unauthorized"
    assert body["message"] == "Invalid or missing authentication token."
    assert body["request_id"]


def test_protected_route_rejects_invalid_token() -> None:
    client = TestClient(create_test_app())

    response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid or missing authentication token."


def test_protected_route_exposes_verified_user() -> None:
    client = TestClient(create_test_app())
    token = make_token()

    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "auth_user_id": "7bdb3f6b-9c01-421a-9d7a-3d1777bbf670",
        "email": "researcher@example.com",
    }
