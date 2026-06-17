import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.llm_service import LLMRequest, LLMResponse, LLMService, LLMServiceError

logger = logging.getLogger(__name__)


class AgentValidationError(ValueError):
    """Raised when an agent receives an unsafe or invalid input payload."""


class AgentExecutionError(RuntimeError):
    """Raised when an agent cannot complete its LLM-backed task safely."""


class AgentFindingOutput(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    severity: str = Field(default="medium", min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    evidence: dict[str, Any] | None = None
    recommendation: str | None = None


class AgentRunResult(BaseModel):
    agent_name: str
    agent_slug: str
    text: str
    raw_output: dict[str, Any]
    findings: list[AgentFindingOutput] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)
    provider: str
    model: str


@dataclass
class BaseAgent:
    name: str
    slug: str
    system_prompt: str
    llm_service: LLMService = field(default_factory=LLMService)
    model: str | None = None
    provider: str | None = None
    temperature: float = 0.2
    json_mode: bool = True
    allowed_input_keys: set[str] | None = None

    def run(self, input_data: Mapping[str, Any]) -> AgentRunResult:
        logger.info("Agent run started.", extra={"agent_slug": self.slug})
        try:
            validated_input = self.validate_input(input_data)
            llm_response = self.call_llm(validated_input)
            result = self.build_result(llm_response)
        except AgentValidationError:
            logger.exception("Agent input validation failed.", extra={"agent_slug": self.slug})
            raise
        except (LLMServiceError, ValidationError, json.JSONDecodeError) as exc:
            logger.exception("Agent run failed.", extra={"agent_slug": self.slug})
            raise AgentExecutionError(f"{self.name} failed to complete.") from exc
        except Exception as exc:
            logger.exception("Unexpected agent run failure.", extra={"agent_slug": self.slug})
            raise AgentExecutionError(f"{self.name} failed to complete.") from exc

        logger.info(
            "Agent run succeeded.",
            extra={"agent_slug": self.slug, "finding_count": len(result.findings)},
        )
        return result

    def validate_input(self, input_data: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(input_data, Mapping):
            raise AgentValidationError("Agent input must be a mapping.")

        normalized = dict(input_data)
        if self.allowed_input_keys is not None:
            unknown_keys = sorted(set(normalized) - self.allowed_input_keys)
            if unknown_keys:
                raise AgentValidationError(f"Agent input includes unsupported keys: {', '.join(unknown_keys)}.")

        return normalized

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        return json.dumps(input_data, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def call_llm(self, input_data: Mapping[str, Any]) -> LLMResponse:
        return self.llm_service.complete(
            LLMRequest(
                system_prompt=self.system_prompt,
                user_prompt=self.build_user_prompt(input_data),
                model=self.model,
                temperature=self.temperature,
                json_mode=self.json_mode,
                provider=self.provider,
            )
        )

    def build_result(self, llm_response: LLMResponse) -> AgentRunResult:
        parsed_output = self.parse_output(llm_response.text)
        findings = self.parse_findings(parsed_output.get("findings", []))
        return AgentRunResult(
            agent_name=self.name,
            agent_slug=self.slug,
            text=llm_response.text,
            raw_output=parsed_output,
            findings=findings,
            usage=llm_response.usage,
            provider=llm_response.provider,
            model=llm_response.model,
        )

    def parse_output(self, output_text: str) -> dict[str, Any]:
        if not output_text.strip():
            raise AgentExecutionError("Agent returned an empty response.")

        parsed = json.loads(output_text)
        if not isinstance(parsed, dict):
            raise AgentExecutionError("Agent response must be a JSON object.")
        return parsed

    def parse_findings(self, findings: Any) -> list[AgentFindingOutput]:
        if findings is None:
            return []
        if not isinstance(findings, list):
            raise AgentExecutionError("Agent findings must be a list.")

        return [AgentFindingOutput.model_validate(finding) for finding in findings]
