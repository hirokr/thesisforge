from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core.errors import install_error_handlers


def test_http_errors_use_standard_shape_and_request_id_header() -> None:
    app = make_app()
    client = TestClient(app)

    response = client.get("/handled", headers={"X-Request-ID": "request-123"})

    assert response.status_code == 400
    assert response.headers["X-Request-ID"] == "request-123"
    assert response.json() == {
        "error": True,
        "code": "bad_request",
        "message": "Bad input.",
        "request_id": "request-123",
    }


def test_validation_errors_use_standard_shape() -> None:
    app = make_app()
    client = TestClient(app)

    response = client.get("/items/not-an-int")

    assert response.status_code == 422
    body = response.json()
    assert body["error"] is True
    assert body["code"] == "validation_error"
    assert body["message"] == "Request validation failed."
    assert body["request_id"]


def test_unhandled_errors_hide_exception_details() -> None:
    app = make_app()
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/unhandled")

    assert response.status_code == 500
    assert response.json()["message"] == "Internal server error."
    assert "secret" not in response.text


def make_app() -> FastAPI:
    app = FastAPI()
    install_error_handlers(app)
    router = APIRouter()

    @router.get("/handled")
    def handled() -> None:
        raise HTTPException(status_code=400, detail="Bad input.")

    @router.get("/items/{item_id}")
    def item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @router.get("/unhandled")
    def unhandled() -> None:
        raise RuntimeError("secret stack detail")

    app.include_router(router)
    return app
