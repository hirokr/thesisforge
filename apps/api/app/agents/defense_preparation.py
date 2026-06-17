import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import AgentFindingOutput, AgentRunResult, BaseAgent
from app.models import AgentFinding
from app.services.llm_service import LLMService


DEFENSE_PREPARATION_SYSTEM_PROMPT = """You are the ThesisForge Defense Preparation Agent.
Generate likely thesis panel questions from prior agent findings and thesis weaknesses.
Return one JSON object with: defense_questions, findings, and handoff_summary.
Each defense question must include question, category, risk_level, and suggested_answer_points.
For a full review, generate at least 8 defense questions."""


class DefensePreparationAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Defense Preparation Agent",
            slug="defense-preparation",
            system_prompt=DEFENSE_PREPARATION_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={"previous_agent_findings", "review_type", "project_context"},
        )

    def run_review(
        self,
        *,
        previous_agent_findings: Iterable[Mapping[str, Any]],
        review_type: str = "full_review",
        project_context: Mapping[str, Any] | None = None,
    ) -> AgentRunResult:
        return self.run(
            {
                "previous_agent_findings": [dict(finding) for finding in previous_agent_findings],
                "review_type": review_type,
                "project_context": dict(project_context or {}),
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        findings = input_data.get("previous_agent_findings") or []
        review_type = str(input_data.get("review_type") or "full_review")
        payload = {
            "task": "Prepare thesis defense questions from the supplied agent findings and project context.",
            "constraints": [
                "For full_review, generate at least 8 defense questions.",
                "Each question must include question, category, risk_level, and suggested_answer_points.",
                "Risk levels must reflect the severity and recurrence of prior findings.",
                "Suggested answer points should help the student defend, qualify, or improve the thesis.",
                "Use only the provided findings and context; do not invent external evidence.",
            ],
            "minimum_question_count": 8 if review_type == "full_review" else 3,
            "missing_previous_findings": not bool(findings),
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("defense_questions", [])
        parsed.setdefault("findings", [])
        parsed.setdefault("handoff_summary", _default_handoff_summary(parsed))
        return parsed

    def save_findings(
        self,
        db: Session,
        *,
        analysis_run_id: UUID,
        agent_id: UUID | None,
        findings: Iterable[AgentFindingOutput],
    ) -> list[AgentFinding]:
        records = [
            AgentFinding(
                analysis_run_id=analysis_run_id,
                agent_id=agent_id,
                category=finding.category,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                evidence=finding.evidence,
                recommendation=finding.recommendation,
            )
            for finding in findings
        ]
        db.add_all(records)
        db.commit()
        for record in records:
            db.refresh(record)
        return records

    def run_and_save(
        self,
        db: Session,
        *,
        analysis_run_id: UUID,
        agent_id: UUID | None,
        previous_agent_findings: Iterable[Mapping[str, Any]],
        review_type: str = "full_review",
        project_context: Mapping[str, Any] | None = None,
    ) -> AgentRunResult:
        result = self.run_review(
            previous_agent_findings=previous_agent_findings,
            review_type=review_type,
            project_context=project_context,
        )
        self.save_findings(
            db,
            analysis_run_id=analysis_run_id,
            agent_id=agent_id,
            findings=result.findings,
        )
        return result

    def handoff_summary(self, result: AgentRunResult) -> str:
        summary = result.raw_output.get("handoff_summary")
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
        return _default_handoff_summary(result.raw_output)


def _default_handoff_summary(parsed: Mapping[str, Any]) -> str:
    questions = parsed.get("defense_questions") or []
    high_risk_count = 0
    for question in questions:
        if isinstance(question, Mapping) and str(question.get("risk_level") or "").lower() == "high":
            high_risk_count += 1
    return f"Prepared {len(questions)} defense questions. High-risk questions: {high_risk_count}."
