import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import AgentFindingOutput, AgentRunResult, BaseAgent
from app.models import AgentFinding
from app.services.llm_service import LLMService


RESULTS_INTERPRETATION_SYSTEM_PROMPT = """You are the ThesisForge Results Interpretation Agent.
Review result summaries against the methodology and objectives. Identify overclaiming,
weak comparisons, missing analysis, and practical discussion points. Return one JSON
object with: results_interpretation_score, overclaiming_warnings,
missing_comparison_warnings, suggested_discussion_points, findings, and handoff_summary."""


class ResultsInterpretationAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Results Interpretation Agent",
            slug="results-interpretation",
            system_prompt=RESULTS_INTERPRETATION_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={
                "results_summary",
                "methodology_summary",
                "objectives",
                "csv_metadata",
                "previous_agent_findings",
            },
        )

    def run_review(
        self,
        *,
        results_summary: str | None,
        methodology_summary: str | None,
        objectives: str | None,
        csv_metadata: Mapping[str, Any] | None = None,
        previous_agent_findings: Iterable[Mapping[str, Any]] = (),
    ) -> AgentRunResult:
        return self.run(
            {
                "results_summary": results_summary or "",
                "methodology_summary": methodology_summary or "",
                "objectives": objectives or "",
                "csv_metadata": dict(csv_metadata or {}),
                "previous_agent_findings": [dict(finding) for finding in previous_agent_findings],
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        results = str(input_data.get("results_summary") or "").strip()
        csv_metadata = input_data.get("csv_metadata") or {}
        payload = {
            "task": "Assess whether the results interpretation is justified by the methodology, objectives, and optional CSV metadata.",
            "constraints": [
                "Handle missing results summaries gracefully with actionable next steps.",
                "Flag claims that exceed the provided evidence.",
                "Use CSV metadata only as summary context; do not infer unseen rows or statistics.",
                "Suggest discussion points that distinguish evidence, limitations, and future work.",
            ],
            "missing_results_summary": not results,
            "has_csv_metadata": bool(csv_metadata),
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("results_interpretation_score", None)
        parsed.setdefault("overclaiming_warnings", [])
        parsed.setdefault("missing_comparison_warnings", [])
        parsed.setdefault("suggested_discussion_points", [])
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
        results_summary: str | None,
        methodology_summary: str | None,
        objectives: str | None,
        csv_metadata: Mapping[str, Any] | None = None,
        previous_agent_findings: Iterable[Mapping[str, Any]] = (),
    ) -> AgentRunResult:
        result = self.run_review(
            results_summary=results_summary,
            methodology_summary=methodology_summary,
            objectives=objectives,
            csv_metadata=csv_metadata,
            previous_agent_findings=previous_agent_findings,
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
    score = parsed.get("results_interpretation_score")
    overclaims = parsed.get("overclaiming_warnings") or []
    comparisons = parsed.get("missing_comparison_warnings") or []
    overclaim_text = "; ".join(str(item) for item in overclaims[:2]) if overclaims else "no overclaiming warnings listed"
    return f"Results interpretation score: {score if score is not None else 'unscored'}. Overclaiming: {overclaim_text}. Missing comparisons: {len(comparisons)}."
