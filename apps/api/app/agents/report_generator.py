import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import AgentRunResult, BaseAgent
from app.models import ActionTask, AnalysisRun, Report, ThesisProject
from app.services.llm_service import LLMService


REPORT_GENERATOR_SYSTEM_PROMPT = """You are the ThesisForge Report Generator Agent.
Synthesize project metadata, agent findings, citation checks, defense questions, and
agent messages into a final thesis health report. Return one JSON object with:
overall_score, score_breakdown, executive_summary, major_risks, priority_fixes,
defense_questions, markdown_report, structured_report, findings, and partial_failures.
The report must be specific, evidence-grounded, and actionable."""


class ReportGeneratorAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Report Generator Agent",
            slug="report-generator",
            system_prompt=REPORT_GENERATOR_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={
                "project_metadata",
                "agent_findings",
                "citation_checks",
                "agent_messages",
                "defense_questions",
                "partial_failures",
            },
        )

    def run_review(
        self,
        *,
        project_metadata: Mapping[str, Any],
        agent_findings: Iterable[Mapping[str, Any]],
        citation_checks: Iterable[Mapping[str, Any]] = (),
        agent_messages: Iterable[Mapping[str, Any]] = (),
        defense_questions: Iterable[Mapping[str, Any]] = (),
        partial_failures: Iterable[Mapping[str, Any] | str] = (),
    ) -> AgentRunResult:
        return self.run(
            {
                "project_metadata": dict(project_metadata),
                "agent_findings": [dict(finding) for finding in agent_findings],
                "citation_checks": [dict(check) for check in citation_checks],
                "agent_messages": [dict(message) for message in agent_messages],
                "defense_questions": [dict(question) for question in defense_questions],
                "partial_failures": list(partial_failures),
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        payload = {
            "task": "Generate the final thesis health report and priority action plan.",
            "constraints": [
                "Return both markdown_report and structured_report.",
                "Include overall_score as a score out of 100 and score_breakdown by review area.",
                "Prioritize fixes by impact on thesis quality and defense risk.",
                "Carry forward defense questions from the Defense Preparation Agent where available.",
                "When an upstream agent failed or returned partial output, list it under partial_failures and continue with available evidence.",
                "Use only supplied project data, findings, citation checks, messages, and defense questions.",
            ],
            "has_partial_failures": bool(input_data.get("partial_failures")),
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("overall_score", None)
        parsed.setdefault("score_breakdown", {})
        parsed.setdefault("executive_summary", "")
        parsed.setdefault("major_risks", [])
        parsed.setdefault("priority_fixes", [])
        parsed.setdefault("defense_questions", [])
        parsed.setdefault("partial_failures", [])
        parsed.setdefault("findings", [])
        parsed.setdefault("structured_report", _default_structured_report(parsed))
        parsed.setdefault("markdown_report", _default_markdown_report(parsed))
        return parsed

    def save_report(
        self,
        db: Session,
        *,
        project: ThesisProject,
        analysis_run: AnalysisRun,
        result: AgentRunResult,
        title: str = "Thesis Health Report",
    ) -> Report:
        raw_output = result.raw_output
        report = Report(
            project_id=project.id,
            analysis_run_id=analysis_run.id,
            title=title,
            status="completed",
            overall_score=_as_float(raw_output.get("overall_score")),
            score_breakdown=_as_dict(raw_output.get("score_breakdown")),
            executive_summary=_as_optional_string(raw_output.get("executive_summary")),
            content=_as_optional_string(raw_output.get("markdown_report")),
            structured_report=_as_dict(raw_output.get("structured_report")) or raw_output,
        )
        db.add(report)
        db.flush()

        for fix in _priority_fix_tasks(raw_output.get("priority_fixes")):
            db.add(
                ActionTask(
                    project_id=project.id,
                    report_id=report.id,
                    title=fix["title"],
                    description=fix.get("description"),
                    category=fix.get("category"),
                    priority=fix.get("priority") or "medium",
                    status="open",
                )
            )

        if report.overall_score is not None:
            project.latest_score = report.overall_score
            analysis_run.overall_score = report.overall_score
        analysis_run.summary = report.executive_summary
        db.commit()
        db.refresh(report)
        return report

    def run_and_save(
        self,
        db: Session,
        *,
        project: ThesisProject,
        analysis_run: AnalysisRun,
        project_metadata: Mapping[str, Any],
        agent_findings: Iterable[Mapping[str, Any]],
        citation_checks: Iterable[Mapping[str, Any]] = (),
        agent_messages: Iterable[Mapping[str, Any]] = (),
        defense_questions: Iterable[Mapping[str, Any]] = (),
        partial_failures: Iterable[Mapping[str, Any] | str] = (),
    ) -> tuple[AgentRunResult, Report]:
        result = self.run_review(
            project_metadata=project_metadata,
            agent_findings=agent_findings,
            citation_checks=citation_checks,
            agent_messages=agent_messages,
            defense_questions=defense_questions,
            partial_failures=partial_failures,
        )
        report = self.save_report(db, project=project, analysis_run=analysis_run, result=result)
        return result, report


def _default_structured_report(parsed: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "overall_score": parsed.get("overall_score"),
        "score_breakdown": parsed.get("score_breakdown") or {},
        "executive_summary": parsed.get("executive_summary") or "",
        "major_risks": parsed.get("major_risks") or [],
        "priority_fixes": parsed.get("priority_fixes") or [],
        "defense_questions": parsed.get("defense_questions") or [],
        "partial_failures": parsed.get("partial_failures") or [],
    }


def _default_markdown_report(parsed: Mapping[str, Any]) -> str:
    summary = parsed.get("executive_summary") or "No executive summary was generated."
    score = parsed.get("overall_score")
    major_risks = parsed.get("major_risks") or []
    fixes = parsed.get("priority_fixes") or []
    risk_lines = "\n".join(f"- {risk}" for risk in major_risks) or "- No major risks listed."
    fix_lines = "\n".join(f"- {_fix_title(fix)}" for fix in fixes) or "- No priority fixes listed."
    return f"# Thesis Health Report\n\nOverall score: {score if score is not None else 'Unscored'}\n\n## Executive Summary\n\n{summary}\n\n## Major Risks\n\n{risk_lines}\n\n## Priority Fixes\n\n{fix_lines}\n"


def _priority_fix_tasks(priority_fixes: Any) -> list[dict[str, str | None]]:
    if not isinstance(priority_fixes, list):
        return []

    tasks: list[dict[str, str | None]] = []
    for fix in priority_fixes:
        if isinstance(fix, str):
            title = fix.strip()
            if title:
                tasks.append({"title": title, "description": None, "category": None, "priority": "medium"})
            continue

        if not isinstance(fix, Mapping):
            continue

        title = _as_optional_string(fix.get("title")) or _as_optional_string(fix.get("task")) or _as_optional_string(fix.get("description"))
        if not title:
            continue
        tasks.append(
            {
                "title": title[:255],
                "description": _as_optional_string(fix.get("description")),
                "category": _as_optional_string(fix.get("category")),
                "priority": _normalize_priority(fix.get("priority")),
            }
        )
    return tasks


def _fix_title(fix: Any) -> str:
    if isinstance(fix, str):
        return fix
    if isinstance(fix, Mapping):
        return str(fix.get("title") or fix.get("task") or fix.get("description") or "Untitled fix")
    return "Untitled fix"


def _normalize_priority(value: Any) -> str:
    priority = str(value or "medium").strip().lower()
    return priority if priority in {"low", "medium", "high", "urgent"} else "medium"


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_dict(value: Any) -> dict[str, Any] | None:
    return dict(value) if isinstance(value, Mapping) else None


def _as_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
