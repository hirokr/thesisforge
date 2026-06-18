from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.services.llm_service import LLMAuthenticationError, LLMRequest, LLMService, LLMServiceError


class FakeCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(
            model=kwargs["model"],
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"status":"ok"}'))],
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=4, total_tokens=16),
        )


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.completions = FakeCompletions()
        self.chat = SimpleNamespace(completions=self.completions)


def test_llm_service_normalizes_openai_response() -> None:
    fake_client = FakeOpenAIClient()
    service = LLMService(
        settings=Settings(openai_api_key="test-key", llm_default_model="gpt-test"),
        openai_client_factory=lambda **kwargs: fake_client,
    )

    response = service.complete(
        LLMRequest(
            system_prompt="You are a thesis reviewer.",
            user_prompt="Review this gap.",
            temperature=0.1,
            json_mode=True,
        )
    )

    assert response.text == '{"status":"ok"}'
    assert response.provider == "openai"
    assert response.model == "gpt-test"
    assert response.usage == {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16}
    assert fake_client.completions.calls == [
        {
            "model": "gpt-test",
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": "You are a thesis reviewer."},
                {"role": "user", "content": "Review this gap."},
            ],
            "response_format": {"type": "json_object"},
        }
    ]


def test_llm_service_allows_per_request_model_override() -> None:
    fake_client = FakeOpenAIClient()
    service = LLMService(
        settings=Settings(openai_api_key="test-key", llm_default_model="gpt-default"),
        openai_client_factory=lambda **kwargs: fake_client,
    )

    response = service.complete(
        LLMRequest(system_prompt="system", user_prompt="user", model="gpt-agent", temperature=0.3)
    )

    assert response.model == "gpt-agent"
    assert fake_client.completions.calls[0]["model"] == "gpt-agent"
    assert "response_format" not in fake_client.completions.calls[0]


def test_llm_service_configures_openai_compatible_base_url() -> None:
    factory_calls: list[dict[str, str]] = []

    def client_factory(*, api_key: str, base_url: str | None = None) -> FakeOpenAIClient:
        factory_calls.append({"api_key": api_key, "base_url": base_url or ""})
        return FakeOpenAIClient()

    service = LLMService(
        settings=Settings(
            openai_api_key="aimlapi-key",
            openai_base_url="https://api.aimlapi.com/v1",
            llm_default_model="gpt-4o",
        ),
        openai_client_factory=client_factory,
    )

    response = service.complete(LLMRequest(system_prompt="system", user_prompt="user"))

    assert response.model == "gpt-4o"
    assert factory_calls == [
        {"api_key": "aimlapi-key", "base_url": "https://api.aimlapi.com/v1"}
    ]


def test_llm_service_rejects_missing_openai_key() -> None:
    service = LLMService(settings=Settings(openai_api_key=""))

    with pytest.raises(LLMServiceError, match="OpenAI API key is not configured"):
        service.complete(LLMRequest(system_prompt="system", user_prompt="user"))


def test_llm_service_wraps_provider_errors_without_secret() -> None:
    def broken_factory(*, api_key: str) -> object:
        raise ValueError(f"bad key {api_key}")

    service = LLMService(
        settings=Settings(openai_api_key="secret-key"),
        openai_client_factory=broken_factory,
    )

    with pytest.raises(LLMServiceError) as exc_info:
        service.complete(LLMRequest(system_prompt="system", user_prompt="user"))

    assert str(exc_info.value) == "LLM provider request failed."
    assert "secret-key" not in str(exc_info.value)


def test_llm_service_classifies_provider_authentication_errors() -> None:
    class AuthenticationFailure(RuntimeError):
        status_code = 401

    class RejectingCompletions:
        def create(self, **kwargs: object) -> object:
            raise AuthenticationFailure("provider response included a secret")

    client = SimpleNamespace(chat=SimpleNamespace(completions=RejectingCompletions()))
    service = LLMService(
        settings=Settings(openai_api_key="secret-key"),
        openai_client_factory=lambda **kwargs: client,
    )

    with pytest.raises(LLMAuthenticationError) as exc_info:
        service.complete(LLMRequest(system_prompt="system", user_prompt="user"))

    assert str(exc_info.value) == "OpenAI authentication failed. Check OPENAI_API_KEY."
    assert "secret-key" not in str(exc_info.value)
