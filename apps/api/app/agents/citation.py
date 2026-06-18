import json
from collections.abc import Iterable, Mapping
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agents.base import AgentFindingOutput, AgentRunResult, BaseAgent
from app.models import AgentFinding, CitationCheck, DocumentChunk, Reference
from app.services.llm_service import LLMService


CITATION_SYSTEM_PROMPT = """You are the ThesisForge Citation Agent.
Compare thesis claims with the provided references and prior literature-review findings.
Return one JSON object with: unsupported_or_weak_claims, citation_checks, findings,
and handoff_summary. Use only the provided references and thesis chunks. Do not claim
external web, DOI, or database verification unless such a tool is explicitly provided."""


class CitationCheckOutput(BaseModel):
    claim_text: str = Field(min_length=1)
    status: str = Field(min_length=1, max_length=50)
    confidence: float | None = Field(default=None, ge=0, le=1)
    notes: str | None = None
    reference_id: str | None = None
    citation_key: str | None = None


class CitationAgent(BaseAgent):
    def __init__(
        self,
        llm_service: LLMService | None = None,
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__(
            name="Citation Agent",
            slug="citation",
            system_prompt=CITATION_SYSTEM_PROMPT,
            llm_service=llm_service or LLMService(),
            model=model,
            provider=provider,
            temperature=temperature,
            json_mode=True,
            allowed_input_keys={"document_chunks", "references", "literature_findings"},
        )

    def run_review(
        self,
        *,
        document_chunks: Iterable[DocumentChunk | Mapping[str, Any]],
        references: Iterable[Reference | Mapping[str, Any]],
        literature_findings: Iterable[Mapping[str, Any]],
    ) -> AgentRunResult:
        return self.run(
            {
                "document_chunks": [_serialize_chunk(chunk) for chunk in document_chunks],
                "references": [_serialize_reference(reference) for reference in references],
                "literature_findings": [dict(finding) for finding in literature_findings],
            }
        )

    def build_user_prompt(self, input_data: Mapping[str, Any]) -> str:
        references = input_data.get("references", [])
        missing_reference_note = (
            "No references were provided. Flag support gaps, but do not infer that claims are false."
            if not references
            else "Assess claim support only against the provided reference metadata and text."
        )
        payload = {
            "task": "Identify thesis claims that are unsupported or weakly supported by the provided references.",
            "constraints": [
                missing_reference_note,
                "Return citation_checks for specific claims that should be tracked in the database.",
                "Use chunk IDs, chunk indexes, reference IDs, and citation keys as evidence when available.",
                "Do not claim external verification, DOI lookup, or web search.",
            ],
            "citation_check_output_contract": {
                "type": "array",
                "item": {
                    "claim_text": "non-empty string",
                    "status": "supported | weakly_supported | unsupported | needs_review",
                    "confidence": "number from 0 to 1, or null",
                    "notes": "string or null",
                    "reference_id": "string or null",
                    "citation_key": "string or null",
                },
            },
            "allowed_citation_check_statuses": ["supported", "weakly_supported", "unsupported", "needs_review"],
            "input": input_data,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    def parse_output(self, output_text: str) -> dict[str, Any]:
        parsed = super().parse_output(output_text)
        parsed.setdefault("unsupported_or_weak_claims", [])
        parsed.setdefault("citation_checks", [])
        parsed.setdefault("findings", [])
        parsed.setdefault("handoff_summary", _default_handoff_summary(parsed))
        parsed["citation_checks"] = [
            check.model_dump()
            for check in (CitationCheckOutput.model_validate(item) for item in parsed["citation_checks"])
        ]
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

    def save_citation_checks(
        self,
        db: Session,
        *,
        analysis_run_id: UUID,
        citation_checks: Iterable[Mapping[str, Any]],
        references: Iterable[Reference | Mapping[str, Any]],
    ) -> list[CitationCheck]:
        reference_lookup = _reference_lookup(references)
        records = [
            CitationCheck(
                analysis_run_id=analysis_run_id,
                reference_id=_resolve_reference_id(check, reference_lookup),
                claim_text=str(check["claim_text"]),
                status=str(check["status"]),
                confidence=check.get("confidence"),
                notes=check.get("notes"),
            )
            for check in citation_checks
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
        document_chunks: Iterable[DocumentChunk | Mapping[str, Any]],
        references: Iterable[Reference | Mapping[str, Any]],
        literature_findings: Iterable[Mapping[str, Any]],
    ) -> AgentRunResult:
        reference_list = list(references)
        result = self.run_review(
            document_chunks=document_chunks,
            references=reference_list,
            literature_findings=literature_findings,
        )
        self.save_findings(
            db,
            analysis_run_id=analysis_run_id,
            agent_id=agent_id,
            findings=result.findings,
        )
        self.save_citation_checks(
            db,
            analysis_run_id=analysis_run_id,
            citation_checks=result.raw_output["citation_checks"],
            references=reference_list,
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


def _reference_lookup(references: Iterable[Reference | Mapping[str, Any]]) -> dict[str, UUID]:
    lookup: dict[str, UUID] = {}
    for reference in references:
        if isinstance(reference, Mapping):
            reference_id = reference.get("id")
            citation_key = reference.get("citation_key")
        else:
            reference_id = reference.id
            citation_key = reference.citation_key

        if isinstance(reference_id, UUID):
            lookup[str(reference_id)] = reference_id
            if citation_key:
                lookup[str(citation_key)] = reference_id
    return lookup


def _resolve_reference_id(check: Mapping[str, Any], lookup: Mapping[str, UUID]) -> UUID | None:
    reference_id = check.get("reference_id")
    citation_key = check.get("citation_key")
    if reference_id is not None and str(reference_id) in lookup:
        return lookup[str(reference_id)]
    if citation_key is not None and str(citation_key) in lookup:
        return lookup[str(citation_key)]
    return None


def _default_handoff_summary(parsed: Mapping[str, Any]) -> str:
    weak_claims = parsed.get("unsupported_or_weak_claims") or []
    checks = parsed.get("citation_checks") or []
    unsupported = sum(1 for check in checks if str(check.get("status", "")).lower() == "unsupported")
    weak_text = "; ".join(str(item) for item in weak_claims[:2]) if weak_claims else "no weak claims listed"
    return f"Citation review checks: {len(checks)}. Unsupported claims: {unsupported}. Priority claims: {weak_text}."
