import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import AgentFindingOutput, AgentRunResult, BaseAgent
from app.models import AgentFinding, DocumentChunk, Reference
from app.services.llm_service import LLMService


LITERATURE_REVIEW_SYSTEM_PROMPT = """You are the ThesisForge Literature Review Agent.
Review thesis context, draft chunks, and provided references. Return one JSON object with:
major_literature_themes, claim_support_observations, weak_or_missing_citation_warnings,
suggested_literature_gaps, findings, and handoff_summary.
Findings must be concise objects with category, severity, title, description, evidence, and recommendation."""


class LiteratureReviewAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Literature Review Agent",
            slug="literature-review",
            system_prompt=LITERATURE_REVIEW_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={"project_context", "references", "document_chunks"},
        )

    def run_review(
        self,
        *,
        project_context: Mapping[str, Any],
        references: Iterable[Reference | Mapping[str, Any]],
        document_chunks: Iterable[DocumentChunk | Mapping[str, Any]],
    ) -> AgentRunResult:
        return self.run(
            {
                "project_context": dict(project_context),
                "references": [_serialize_reference(reference) for reference in references],
                "document_chunks": [_serialize_chunk(chunk) for chunk in document_chunks],
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        references = input_data.get("references", [])
        missing_reference_note = (
            "No references were provided. Review the draft gracefully and flag citation support gaps without claiming external verification."
            if not references
            else "Use only the provided reference metadata for citation-support observations."
        )
        payload = {
            "task": "Evaluate literature coverage, citation support, and possible literature gaps.",
            "constraints": [
                missing_reference_note,
                "Do not claim web or external database verification.",
                "Use document chunk IDs as evidence when available.",
            ],
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("major_literature_themes", [])
        parsed.setdefault("claim_support_observations", [])
        parsed.setdefault("weak_or_missing_citation_warnings", [])
        parsed.setdefault("suggested_literature_gaps", [])
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
        project_context: Mapping[str, Any],
        references: Iterable[Reference | Mapping[str, Any]],
        document_chunks: Iterable[DocumentChunk | Mapping[str, Any]],
    ) -> AgentRunResult:
        result = self.run_review(
            project_context=project_context,
            references=references,
            document_chunks=document_chunks,
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


def _serialize_reference(reference: Reference | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(reference, Mapping):
        return dict(reference)
    return {
        "id": str(reference.id),
        "citation_key": reference.citation_key,
        "title": reference.title,
        "authors": reference.authors or [],
        "year": reference.year,
        "venue": reference.venue,
        "doi": reference.doi,
        "url": reference.url,
        "citation_text": reference.citation_text,
    }


def _serialize_chunk(chunk: DocumentChunk | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(chunk, Mapping):
        return dict(chunk)
    return {
        "id": str(chunk.id),
        "document_id": str(chunk.document_id),
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
    }


def _default_handoff_summary(parsed: Mapping[str, Any]) -> str:
    themes = parsed.get("major_literature_themes") or []
    gaps = parsed.get("suggested_literature_gaps") or []
    warning_count = len(parsed.get("weak_or_missing_citation_warnings") or [])
    theme_text = "; ".join(str(theme) for theme in themes[:3]) if themes else "No dominant themes identified"
    gap_text = "; ".join(str(gap) for gap in gaps[:2]) if gaps else "no specific literature gaps suggested"
    return f"Literature review themes: {theme_text}. Citation warnings: {warning_count}. Suggested gaps: {gap_text}."
