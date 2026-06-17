import logging
from http import HTTPStatus
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger("thesisforge.errors")


def install_error_handlers(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_id(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = get_request_id(request)
        message = exc.detail if isinstance(exc.detail, str) else default_message(exc.status_code)
        log_handled_error(request, request_id, exc.status_code, message)
        return error_response(exc.status_code, message, request_id, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = get_request_id(request)
        logger.info(
            "Validation error request_id=%s method=%s path=%s errors=%s",
            request_id,
            request.method,
            request.url.path,
            exc.errors(),
        )
        return error_response(422, "Request validation failed.", request_id, code="validation_error")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = get_request_id(request)
        logger.exception(
            "Unhandled error request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return error_response(500, "Internal server error.", request_id)


def error_response(
    status_code: int,
    message: str,
    request_id: str,
    *,
    code: str | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "code": code or code_for_status(status_code),
            "message": message,
            "request_id": request_id,
        },
        headers=headers,
    )


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", str(uuid4()))


def log_handled_error(request: Request, request_id: str, status_code: int, message: str) -> None:
    if status_code >= 500:
        logger.error("HTTP error request_id=%s method=%s path=%s status=%s", request_id, request.method, request.url.path, status_code)
        return

    logger.info(
        "HTTP error request_id=%s method=%s path=%s status=%s message=%s",
        request_id,
        request.method,
        request.url.path,
        status_code,
        message,
    )


def default_message(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Request failed."


def code_for_status(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        413: "payload_too_large",
        422: "validation_error",
        500: "internal_server_error",
    }
    return mapping.get(status_code, f"http_{status_code}")
