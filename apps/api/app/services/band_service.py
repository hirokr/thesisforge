import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import quote

import httpx

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class BandServiceError(RuntimeError):
    """Raised when a Band API request cannot be completed safely."""


class BandHTTPClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        ...


@dataclass(frozen=True)
class BandPeer:
    id: str
    name: str | None = None
    handle: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BandService:
    settings: Settings | None = None
    http_client: BandHTTPClient | None = None
    timeout_seconds: float = 20.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "settings", self.settings or get_settings())

    def validate_agent_identity(self) -> dict[str, Any]:
        return self._request("GET", "/me")

    def create_chat(self, task_id: str, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", "/chats", {"chat": {}})

    def list_peers(self) -> list[BandPeer]:
        payload = self._request("GET", "/peers")
        items = payload.get("items", []) if isinstance(payload, Mapping) else []
        return [_normalize_peer(item) for item in items if isinstance(item, Mapping) and item.get("id")]

    def add_participant(self, chat_id: str, participant_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/chats/{_path_part(chat_id)}/participants",
            {"participant": {"id": participant_id}},
        )

    def send_message(
        self,
        chat_id: str,
        content: str,
        mentions: list[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        message: dict[str, Any] = {"content": content}
        if mentions:
            message["mentions"] = [dict(mention) for mention in mentions]
        return self._request("POST", f"/chats/{_path_part(chat_id)}/messages", {"message": message})

    def post_event(
        self,
        chat_id: str,
        content: str,
        message_type: str = "task",
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        event: dict[str, Any] = {"content": content, "message_type": message_type}
        if metadata:
            event["metadata"] = dict(metadata)
        return self._request("POST", f"/chats/{_path_part(chat_id)}/events", {"event": event})

    def fetch_context(self, chat_id: str) -> dict[str, Any]:
        return self._request("GET", f"/chats/{_path_part(chat_id)}/context")

    def _request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        settings = self.settings or get_settings()
        if not settings.band_api_key:
            raise BandServiceError("Band API key is not configured.")
        if not settings.band_api_base_url:
            raise BandServiceError("Band API base URL is not configured.")

        url = f"{settings.band_api_base_url.rstrip('/')}/{path.lstrip('/')}"
        logger.info("Starting Band API request.", extra={"method": method, "path": path})

        try:
            response = self._send_request(method, url, payload)
        except BandServiceError:
            raise
        except httpx.HTTPError as exc:
            logger.exception("Band API network request failed.", extra={"method": method, "path": path})
            raise BandServiceError("Band API request failed.") from exc
        except Exception as exc:
            logger.exception("Band API request failed.", extra={"method": method, "path": path})
            raise BandServiceError("Band API request failed.") from exc

        status_code = int(getattr(response, "status_code", 0) or 0)
        if status_code >= 400:
            logger.warning("Band API returned an error.", extra={"method": method, "path": path, "status_code": status_code})
            raise BandServiceError(f"Band API request failed with status {status_code}.")

        logger.info("Band API request succeeded.", extra={"method": method, "path": path})
        return _response_json(response)

    def _send_request(self, method: str, url: str, payload: Mapping[str, Any] | None) -> Any:
        settings = self.settings or get_settings()
        headers = {"X-API-Key": settings.band_api_key}
        if self.http_client is not None:
            return self.http_client.request(
                method,
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )

        with httpx.Client() as client:
            return client.request(
                method,
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )


def _normalize_peer(item: Mapping[str, Any]) -> BandPeer:
    return BandPeer(
        id=str(item["id"]),
        name=str(item["name"]) if item.get("name") is not None else None,
        handle=str(item["handle"]) if item.get("handle") is not None else None,
        raw=dict(item),
    )


def _response_json(response: Any) -> dict[str, Any]:
    if int(getattr(response, "status_code", 0) or 0) == 204:
        return {}

    try:
        payload = response.json()
    except ValueError:
        return {}

    if not isinstance(payload, Mapping):
        return {"items": payload}

    data = payload.get("data")
    if isinstance(data, Mapping):
        return dict(data)
    if isinstance(data, list):
        return {"items": data}
    return dict(payload)


def _path_part(value: str) -> str:
    return quote(value, safe="")
