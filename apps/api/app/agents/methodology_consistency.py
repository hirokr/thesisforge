import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import AgentFindingOutput, AgentRunResult, BaseAgent
from app.models import AgentFinding
from app.services.llm_service import LLMService


METHODOLOGY_CONSISTENCY_SYSTEM_PROMPT = """You are the ThesisForge Methodology Consistency Agent.
Check whether the methodology aligns with the research gap, objectives, datasets,
and results. Return one JSON object with: methodology_consistency_score,
mismatch_warnings, missing_baselines_or_ablations, suggested_fixes, findings,
and handoff_summary."""


class MethodologyConsistencyAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Methodology Consistency Agent",
            slug="methodology-consistency",
            system_prompt=METHODOLOGY_CONSISTENCY_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={
                "research_gap",
                "objectives",
                "methodology_summary",
                "dataset_summary",
                "results_summary",
                "previous_agent_findings",
            },
        )

    def run_review(
        self,
        *,
        research_gap: str | None,
        objectives: str | None,
        methodology_summary: str | None,
        dataset_summary: str | None,
        results_summary: str | None,
        previous_agent_findings: Iterable[Mapping[str, Any]],
    ) -> AgentRunResult:
        return self.run(
            {
                "research_gap": research_gap or "",
                "objectives": objectives or "",
                "methodology_summary": methodology_summary or "",
                "dataset_summary": dataset_summary or "",
                "results_summary": results_summary or "",
                "previous_agent_findings": [dict(finding) for finding in previous_agent_findings],
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        methodology = str(input_data.get("methodology_summary") or "").strip()
        dataset = str(input_data.get("dataset_summary") or "").strip()
        payload = {
            "task": "Evaluate methodology alignment against the stated gap, objectives, dataset, and results.",
            "constraints": [
                "Return actionable methodology fixes suitable for a thesis student.",
                "Use previous agent findings only as context; do not invent experimental evidence.",
                "Flag missing baselines, ablations, datasets, or evaluation details when they affect claim strength.",
            ],
            "missing_methodology_summary": not methodology,
            "missing_dataset_summary": not dataset,
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("methodology_consistency_score", None)
        parsed.setdefault("mismatch_warnings", [])
        parsed.setdefault("missing_baselines_or_ablations", [])
        parsed.setdefault("suggested_fixes", [])
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
        research_gap: str | None,
        objectives: str | None,
        methodology_summary: str | None,
        dataset_summary: str | None,
        results_summary: str | None,
        previous_agent_findings: Iterable[Mapping[str, Any]],
    ) -> AgentRunResult:
        result = self.run_review(
            research_gap=research_gap,
            objectives=objectives,
            methodology_summary=methodology_summary,
            dataset_summary=dataset_summary,
            results_summary=results_summary,
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
    score = parsed.get("methodology_consistency_score")
    mismatches = parsed.get("mismatch_warnings") or []
    missing = parsed.get("missing_baselines_or_ablations") or []
    mismatch_text = "; ".join(str(item) for item in mismatches[:2]) if mismatches else "no major mismatches listed"
    return f"Methodology consistency score: {score if score is not None else 'unscored'}. Mismatches: {mismatch_text}. Missing baselines or ablations: {len(missing)}."
