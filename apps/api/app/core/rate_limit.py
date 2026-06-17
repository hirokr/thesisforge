import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import DefaultDict

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.config import get_settings

logger = logging.getLogger("thesisforge.rate_limit")


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    limit_setting: str


_requests: DefaultDict[str, deque[float]] = defaultdict(deque)


def rate_limit(rule: RateLimitRule) -> Callable[..., None]:
    def dependency(
        request: Request,
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> None:
        settings = get_settings()
        window_seconds = max(1, settings.rate_limit_window_seconds)
        max_requests = max(1, int(getattr(settings, rule.limit_setting)))
        now = time.monotonic()
        identity = current_user.auth_user_id or _client_ip(request)
        key = f"{rule.name}:{identity}"
        bucket = _requests[key]

        while bucket and now - bucket[0] >= window_seconds:
            bucket.popleft()

        if len(bucket) >= max_requests:
            logger.warning(
                "Rate limit exceeded route_group=%s user_id=%s ip=%s limit=%s window_seconds=%s",
                rule.name,
                current_user.auth_user_id,
                _client_ip(request),
                max_requests,
                window_seconds,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please wait a moment and try again.",
                headers={"Retry-After": str(window_seconds)},
            )

        bucket.append(now)

    return dependency


def clear_rate_limit_state() -> None:
    _requests.clear()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


file_upload_rate_limit = rate_limit(
    RateLimitRule(name="file_upload", limit_setting="rate_limit_file_uploads_per_window")
)
analysis_run_rate_limit = rate_limit(
    RateLimitRule(name="analysis_run", limit_setting="rate_limit_analysis_runs_per_window")
)
