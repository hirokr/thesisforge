import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import AgentFindingOutput, AgentRunResult, BaseAgent
from app.models import AgentFinding
from app.services.llm_service import LLMService


RESEARCH_GAP_SYSTEM_PROMPT = """You are the ThesisForge Research Gap Agent.
Evaluate whether the research gap is clear, specific, supported by literature findings,
and aligned with the problem statement and objectives. Return one JSON object with:
gap_quality_score, weaknesses, improved_research_gap_suggestion, missing_evidence,
findings, and handoff_summary."""


class ResearchGapAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Research Gap Agent",
            slug="research-gap",
            system_prompt=RESEARCH_GAP_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={"problem_statement", "research_gap", "objectives", "literature_findings"},
        )

    def run_review(
        self,
        *,
        problem_statement: str | None,
        research_gap: str | None,
        objectives: str | None,
        literature_findings: Iterable[Mapping[str, Any]],
    ) -> AgentRunResult:
        return self.run(
            {
                "problem_statement": problem_statement or "",
                "research_gap": research_gap or "",
                "objectives": objectives or "",
                "literature_findings": [dict(finding) for finding in literature_findings],
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        gap = str(input_data.get("research_gap") or "").strip()
        payload = {
            "task": "Assess research-gap clarity, specificity, support, and alignment.",
            "constraints": [
                "Return actionable feedback suitable for a thesis student.",
                "Use the provided literature findings only; do not claim external verification.",
                "If the research gap is empty, explain what evidence and specificity are missing.",
            ],
            "empty_research_gap": not gap,
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("gap_quality_score", None)
        parsed.setdefault("weaknesses", [])
        parsed.setdefault("improved_research_gap_suggestion", "")
        parsed.setdefault("missing_evidence", [])
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
        problem_statement: str | None,
        research_gap: str | None,
        objectives: str | None,
        literature_findings: Iterable[Mapping[str, Any]],
    ) -> AgentRunResult:
        result = self.run_review(
            problem_statement=problem_statement,
            research_gap=research_gap,
            objectives=objectives,
            literature_findings=literature_findings,
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
    score = parsed.get("gap_quality_score")
    weaknesses = parsed.get("weaknesses") or []
    missing_evidence = parsed.get("missing_evidence") or []
    weakness_text = "; ".join(str(item) for item in weaknesses[:2]) if weaknesses else "no major weaknesses listed"
    return f"Research gap score: {score if score is not None else 'unscored'}. Weaknesses: {weakness_text}. Missing evidence items: {len(missing_evidence)}."
