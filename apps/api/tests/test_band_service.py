from dataclasses import dataclass
from typing import Any

import pytest

from app.core.config import Settings
from app.services.band_service import BandService, BandServiceError


@dataclass
class FakeResponse:
    status_code: int
    payload: object

    def json(self) -> object:
        return self.payload


class FakeBandClient:
    def __init__(self, response: FakeResponse | None = None) -> None:
        self.response = response or FakeResponse(200, {"id": "ok"})
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        return self.response


def make_service(client: FakeBandClient, **settings_overrides: object) -> BandService:
    settings = Settings(
        band_api_base_url="https://band.test/api/v1/agent",
        band_api_key="secret-band-key",
        **settings_overrides,
    )
    return BandService(settings=settings, http_client=client)


def test_validate_agent_identity_calls_band_me_endpoint() -> None:
    client = FakeBandClient(FakeResponse(200, {"id": "agent-id", "name": "Research Gap Agent"}))
    service = make_service(client)

    response = service.validate_agent_identity()

    assert response == {"id": "agent-id", "name": "Research Gap Agent"}
    assert client.calls == [
        {
            "method": "GET",
            "url": "https://band.test/api/v1/agent/me",
            "headers": {"X-API-Key": "secret-band-key"},
            "json": None,
            "timeout": 20.0,
        }
    ]


def test_create_chat_sends_task_and_project_metadata() -> None:
    client = FakeBandClient(FakeResponse(201, {"id": "chat-id", "task_id": "run-id"}))
    service = make_service(client, band_project_id="project-id")

    response = service.create_chat("run-id", metadata={"source": "thesisforge"})

    assert response["id"] == "chat-id"
    assert client.calls[0]["method"] == "POST"
    assert client.calls[0]["url"] == "https://band.test/api/v1/agent/chats"
    assert client.calls[0]["json"] == {
        "chat": {
            "task_id": "run-id",
            "project_id": "project-id",
            "metadata": {"source": "thesisforge"},
        }
    }


def test_list_peers_normalizes_items() -> None:
    client = FakeBandClient(
        FakeResponse(
            200,
            {
                "items": [
                    {"id": "peer-1", "name": "Methodology Agent", "handle": "methodology_agent"},
                    {"name": "missing id"},
                ]
            },
        )
    )
    service = make_service(client)

    peers = service.list_peers()

    assert len(peers) == 1
    assert peers[0].id == "peer-1"
    assert peers[0].handle == "methodology_agent"


def test_chat_actions_use_expected_band_payloads() -> None:
    client = FakeBandClient(FakeResponse(200, {"id": "ok"}))
    service = make_service(client)

    service.add_participant("chat/id", "peer-id")
    service.send_message(
        "chat/id",
        "@research_gap_agent please review",
        mentions=[{"id": "peer-id", "name": "Research Gap Agent", "handle": "research_gap_agent"}],
    )
    service.post_event("chat/id", "Citation Agent started", metadata={"agent": "citation_agent"})
    service.fetch_context("chat/id")

    assert [call["url"] for call in client.calls] == [
        "https://band.test/api/v1/agent/chats/chat%2Fid/participants",
        "https://band.test/api/v1/agent/chats/chat%2Fid/messages",
        "https://band.test/api/v1/agent/chats/chat%2Fid/events",
        "https://band.test/api/v1/agent/chats/chat%2Fid/context",
    ]
    assert client.calls[0]["json"] == {"participant": {"id": "peer-id"}}
    assert client.calls[1]["json"] == {
        "message": {
            "content": "@research_gap_agent please review",
            "mentions": [{"id": "peer-id", "name": "Research Gap Agent", "handle": "research_gap_agent"}],
        }
    }
    assert client.calls[2]["json"] == {
        "event": {
            "content": "Citation Agent started",
            "message_type": "task",
            "metadata": {"agent": "citation_agent"},
        }
    }
    assert client.calls[3]["method"] == "GET"


def test_band_service_rejects_missing_api_key() -> None:
    service = BandService(settings=Settings(band_api_key=""), http_client=FakeBandClient())

    with pytest.raises(BandServiceError, match="Band API key is not configured"):
        service.validate_agent_identity()


def test_band_service_wraps_failures_without_secret() -> None:
    client = FakeBandClient(FakeResponse(403, {"detail": "bad key secret-band-key"}))
    service = make_service(client)

    with pytest.raises(BandServiceError) as exc_info:
        service.validate_agent_identity()

    assert str(exc_info.value) == "Band API request failed with status 403."
    assert "secret-band-key" not in str(exc_info.value)
