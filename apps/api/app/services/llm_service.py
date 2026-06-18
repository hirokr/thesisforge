import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMServiceError(RuntimeError):
    """Raised when an LLM request cannot be completed safely."""


class LLMAuthenticationError(LLMServiceError):
    """Raised when the configured provider credential is rejected."""


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str
    model: str | None = None
    temperature: float = 0.2
    json_mode: bool = False
    provider: str | None = None


@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: dict[str, Any] = field(default_factory=dict)
    provider: str = "openai"
    model: str = ""


class OpenAIClientFactory(Protocol):
    def __call__(self, *, api_key: str, base_url: str | None = None) -> Any:
        ...


class LLMService:
    def __init__(
        self,
        settings: Settings | None = None,
        openai_client_factory: OpenAIClientFactory | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._openai_client_factory = openai_client_factory

    def complete(self, request: LLMRequest) -> LLMResponse:
        provider = (request.provider or self.settings.llm_default_provider).lower()
        if provider != "openai":
            raise LLMServiceError(f"Unsupported LLM provider: {provider}.")

        model = request.model or self.settings.llm_default_model
        logger.info("Starting LLM request.", extra={"provider": provider, "model": model})
        try:
            response = self._complete_with_openai(request, model)
        except LLMServiceError:
            logger.exception("LLM request failed.", extra={"provider": provider, "model": model})
            raise
        except Exception as exc:
            logger.exception("LLM provider request failed.", extra={"provider": provider, "model": model})
            if getattr(exc, "status_code", None) == 401:
                raise LLMAuthenticationError("OpenAI authentication failed. Check OPENAI_API_KEY.") from exc
            raise LLMServiceError("LLM provider request failed.") from exc

        logger.info("LLM request succeeded.", extra={"provider": provider, "model": model})
        return response

    def _complete_with_openai(self, request: LLMRequest, model: str) -> LLMResponse:
        if not self.settings.openai_api_key:
            raise LLMServiceError("OpenAI API key is not configured.")

        client = self._get_openai_client()
        payload: dict[str, Any] = {
            "model": model,
            "temperature": request.temperature,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        }
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}

        completion = client.chat.completions.create(**payload)
        text = _extract_text(completion)
        usage = _normalize_usage(getattr(completion, "usage", None))
        returned_model = str(getattr(completion, "model", model) or model)
        return LLMResponse(text=text, usage=usage, provider="openai", model=returned_model)

    def _get_openai_client(self) -> Any:
        base_url = self.settings.openai_base_url.strip() or None
        if self._openai_client_factory is not None:
            return self._openai_client_factory(api_key=self.settings.openai_api_key, base_url=base_url)

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMServiceError("OpenAI SDK is not installed.") from exc

        return OpenAI(api_key=self.settings.openai_api_key, base_url=base_url)


def _extract_text(completion: Any) -> str:
    choices = getattr(completion, "choices", None) or []
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", "") if message is not None else ""
    return content or ""


def _normalize_usage(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if isinstance(usage, Mapping):
        return dict(usage)
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    return {
        key: value
        for key, value in vars(usage).items()
        if not key.startswith("_") and isinstance(key, str)
    }
