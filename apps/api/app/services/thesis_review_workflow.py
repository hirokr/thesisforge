import logging
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.agents.base import AgentExecutionError, AgentRunResult
from app.agents.citation import CitationAgent
from app.agents.defense_preparation import DefensePreparationAgent
from app.agents.literature_review import LiteratureReviewAgent
from app.agents.methodology_consistency import MethodologyConsistencyAgent
from app.agents.report_generator import ReportGeneratorAgent
from app.agents.research_gap import ResearchGapAgent
from app.agents.results_interpretation import ResultsInterpretationAgent
from app.models import Agent, AgentMessage, AnalysisRun, CitationCheck, Document, DocumentChunk, Reference, Report, ThesisProject
from app.services.agent_messages import AgentMessageCreate, create_local_agent_message, send_agent_message_via_band
from app.services.band_service import BandService, BandServiceError
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

WORKFLOW_AGENT_SLUGS = (
    "literature-review",
    "research-gap",
    "citation",
    "methodology-consistency",
    "results-interpretation",
    "defense-preparation",
    "report-generator",
)


class ThesisReviewWorkflowError(RuntimeError):
    """Raised when a thesis review workflow cannot complete its required final step."""


@dataclass
class WorkflowOptions:
    include_results_agent: bool = True
    use_band: bool = True


@dataclass
class WorkflowAgentFailure:
    agent_slug: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"agent_slug": self.agent_slug, "message": self.message}


@dataclass
class ThesisReviewWorkflowResult:
    analysis_run: AnalysisRun
    report: Report | None
    agent_results: dict[str, AgentRunResult] = field(default_factory=dict)
    partial_failures: list[WorkflowAgentFailure] = field(default_factory=list)


AgentFactory = Callable[[Agent | None], Any]


class ThesisReviewWorkflow:
    def __init__(
        self,
        *,
        llm_service: LLMService | None = None,
        band_service: BandService | None = None,
        agent_factories: Mapping[str, AgentFactory] | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.band_service = band_service or BandService()
        self.agent_factories = dict(agent_factories or _default_agent_factories(self.llm_service))

    def run(
        self,
        db: Session,
        *,
        analysis_run_id: UUID,
        options: WorkflowOptions | None = None,
    ) -> ThesisReviewWorkflowResult:
        options = options or WorkflowOptions()
        analysis_run = _load_analysis_run(db, analysis_run_id)
        project = analysis_run.project
        agents_by_slug = _load_agents(db)
        state = _WorkflowState(analysis_run=analysis_run, project=project, agents_by_slug=agents_by_slug)

        self._mark_running(db, analysis_run)
        chat_id = self._create_band_chat(analysis_run, project, options)
        chunks = _load_document_chunks(db, project.id)
        references = _load_references(db, project.id)
        csv_metadata = _load_csv_metadata(db, project.id)
        project_context = _project_context(project)

        self._run_literature_review(db, state, project_context, references, chunks)
        self._handoff(db, state, chat_id, "literature-review", "research-gap", options)

        self._run_research_gap(db, state)
        self._handoff(db, state, chat_id, "research-gap", "citation", options)

        self._run_citation(db, state, references, chunks)
        self._handoff(db, state, chat_id, "citation", "methodology-consistency", options)

        self._run_methodology(db, state)

        if options.include_results_agent:
            self._handoff(db, state, chat_id, "methodology-consistency", "results-interpretation", options)
            self._run_results(db, state, csv_metadata)
            self._handoff(db, state, chat_id, "results-interpretation", "defense-preparation", options)
        else:
            self._handoff(db, state, chat_id, "methodology-consistency", "defense-preparation", options)

        self._run_defense(db, state, project_context)
        self._handoff(db, state, chat_id, "defense-preparation", "report-generator", options)

        report = self._run_report(db, state, project_context)
        self._mark_completed(db, analysis_run)
        return ThesisReviewWorkflowResult(
            analysis_run=analysis_run,
            report=report,
            agent_results=state.agent_results,
            partial_failures=state.partial_failures,
        )

    def _run_literature_review(
        self,
        db: Session,
        state: "_WorkflowState",
        project_context: Mapping[str, Any],
        references: Iterable[Reference],
        chunks: Iterable[DocumentChunk],
    ) -> None:
        agent = self._build_agent("literature-review", state)
        self._run_agent(
            db,
            state,
            "literature-review",
            lambda: agent.run_and_save(
                db,
                analysis_run_id=state.analysis_run.id,
                agent_id=_agent_id(state, "literature-review"),
                project_context=project_context,
                references=references,
                document_chunks=chunks,
            ),
        )

    def _run_research_gap(self, db: Session, state: "_WorkflowState") -> None:
        agent = self._build_agent("research-gap", state)
        self._run_agent(
            db,
            state,
            "research-gap",
            lambda: agent.run_and_save(
                db,
                analysis_run_id=state.analysis_run.id,
                agent_id=_agent_id(state, "research-gap"),
                problem_statement=state.project.problem_statement,
                research_gap=state.project.research_gap,
                objectives=state.project.objectives,
                literature_findings=_result_findings(state, "literature-review"),
            ),
        )

    def _run_citation(
        self,
        db: Session,
        state: "_WorkflowState",
        references: Iterable[Reference],
        chunks: Iterable[DocumentChunk],
    ) -> None:
        agent = self._build_agent("citation", state)
        self._run_agent(
            db,
            state,
            "citation",
            lambda: agent.run_and_save(
                db,
                analysis_run_id=state.analysis_run.id,
                agent_id=_agent_id(state, "citation"),
                document_chunks=chunks,
                references=references,
                literature_findings=_result_findings(state, "literature-review"),
            ),
        )

    def _run_methodology(self, db: Session, state: "_WorkflowState") -> None:
        agent = self._build_agent("methodology-consistency", state)
        self._run_agent(
            db,
            state,
            "methodology-consistency",
            lambda: agent.run_and_save(
                db,
                analysis_run_id=state.analysis_run.id,
                agent_id=_agent_id(state, "methodology-consistency"),
                research_gap=state.project.research_gap,
                objectives=state.project.objectives,
                methodology_summary=state.project.methodology_summary,
                dataset_summary=state.project.dataset_summary,
                results_summary=state.project.results_summary,
                previous_agent_findings=_all_result_findings(state),
            ),
        )

    def _run_results(self, db: Session, state: "_WorkflowState", csv_metadata: Mapping[str, Any] | None) -> None:
        agent = self._build_agent("results-interpretation", state)
        self._run_agent(
            db,
            state,
            "results-interpretation",
            lambda: agent.run_and_save(
                db,
                analysis_run_id=state.analysis_run.id,
                agent_id=_agent_id(state, "results-interpretation"),
                results_summary=state.project.results_summary,
                methodology_summary=state.project.methodology_summary,
                objectives=state.project.objectives,
                csv_metadata=csv_metadata,
                previous_agent_findings=_all_result_findings(state),
            ),
        )

    def _run_defense(self, db: Session, state: "_WorkflowState", project_context: Mapping[str, Any]) -> None:
        agent = self._build_agent("defense-preparation", state)
        self._run_agent(
            db,
            state,
            "defense-preparation",
            lambda: agent.run_and_save(
                db,
                analysis_run_id=state.analysis_run.id,
                agent_id=_agent_id(state, "defense-preparation"),
                previous_agent_findings=_all_result_findings(state),
                review_type="full_review",
                project_context=project_context,
            ),
        )

    def _run_report(self, db: Session, state: "_WorkflowState", project_context: Mapping[str, Any]) -> Report:
        agent = self._build_agent("report-generator", state)
        try:
            result, report = agent.run_and_save(
                db,
                project=state.project,
                analysis_run=state.analysis_run,
                project_metadata=project_context,
                agent_findings=_all_result_findings(state),
                citation_checks=_serialize_citation_checks(_load_citation_checks(db, state.analysis_run.id)),
                agent_messages=_serialize_agent_messages(_load_agent_messages(db, state.analysis_run.id)),
                defense_questions=_defense_questions(state),
                partial_failures=[failure.as_dict() for failure in state.partial_failures],
            )
        except Exception as exc:
            self._record_failure(db, state, "report-generator", exc)
            self._mark_failed(db, state.analysis_run, "Report generation failed.")
            raise ThesisReviewWorkflowError("Thesis review workflow failed during report generation.") from exc

        state.agent_results["report-generator"] = result
        return report

    def _run_agent(
        self,
        db: Session,
        state: "_WorkflowState",
        agent_slug: str,
        runner: Callable[[], AgentRunResult],
    ) -> None:
        try:
            state.agent_results[agent_slug] = runner()
        except AgentExecutionError as exc:
            self._record_failure(db, state, agent_slug, exc)
        except Exception as exc:
            self._record_failure(db, state, agent_slug, exc)

    def _record_failure(self, db: Session, state: "_WorkflowState", agent_slug: str, exc: Exception) -> None:
        logger.exception("Workflow agent failed.", extra={"agent_slug": agent_slug, "analysis_run_id": str(state.analysis_run.id)})
        failure = WorkflowAgentFailure(agent_slug=agent_slug, message=str(exc) or "Agent failed.")
        state.partial_failures.append(failure)
        create_local_agent_message(
            db,
            AgentMessageCreate(
                analysis_run_id=state.analysis_run.id,
                project_id=state.project.id,
                from_agent_id=_agent_id(state, agent_slug),
                message_type="agent_failure",
                task=f"{agent_slug}_failed",
                summary=f"{_display_agent_name(agent_slug)} failed; workflow will continue with available context.",
                payload=failure.as_dict(),
                metadata={"analysis_run_id": str(state.analysis_run.id), "agent_slug": agent_slug},
            ),
            status="failed",
        )

    def _handoff(
        self,
        db: Session,
        state: "_WorkflowState",
        chat_id: str | None,
        from_slug: str,
        to_slug: str,
        options: WorkflowOptions,
    ) -> None:
        result = state.agent_results.get(from_slug)
        if result is None:
            return

        summary = _handoff_summary(self._build_agent(from_slug, state), result)
        message = AgentMessageCreate(
            analysis_run_id=state.analysis_run.id,
            project_id=state.project.id,
            from_agent_id=_agent_id(state, from_slug),
            to_agent_id=_agent_id(state, to_slug),
            message_type="handoff",
            task=f"{from_slug}_to_{to_slug}",
            summary=summary,
            payload={"from_agent": from_slug, "to_agent": to_slug, "raw_output": result.raw_output},
            content=summary,
            metadata={"analysis_run_id": str(state.analysis_run.id), "project_id": str(state.project.id)},
        )
        if options.use_band and chat_id:
            send_agent_message_via_band(db, band_service=self.band_service, chat_id=chat_id, message=message)
        else:
            create_local_agent_message(db, message, status="sent" if not options.use_band else "failed")

    def _create_band_chat(
        self,
        analysis_run: AnalysisRun,
        project: ThesisProject,
        options: WorkflowOptions,
    ) -> str | None:
        if not options.use_band:
            return None
        try:
            response = self.band_service.create_chat(
                str(analysis_run.id),
                metadata={"project_id": str(project.id), "project_title": project.title},
            )
        except BandServiceError:
            logger.warning("Band chat creation failed; workflow will keep local messages.", extra={"analysis_run_id": str(analysis_run.id)})
            return None
        value = response.get("id") or response.get("chat_id")
        return str(value) if value is not None else None

    def _build_agent(self, slug: str, state: "_WorkflowState") -> Any:
        factory = self.agent_factories[slug]
        return factory(state.agents_by_slug.get(slug))

    def _mark_running(self, db: Session, analysis_run: AnalysisRun) -> None:
        analysis_run.status = "running"
        analysis_run.started_at = analysis_run.started_at or datetime.now(UTC)
        db.commit()
        db.refresh(analysis_run)

    def _mark_completed(self, db: Session, analysis_run: AnalysisRun) -> None:
        analysis_run.status = "completed"
        analysis_run.completed_at = datetime.now(UTC)
        db.commit()
        db.refresh(analysis_run)

    def _mark_failed(self, db: Session, analysis_run: AnalysisRun, summary: str) -> None:
        analysis_run.status = "failed"
        analysis_run.summary = summary
        analysis_run.completed_at = datetime.now(UTC)
        db.commit()
        db.refresh(analysis_run)


@dataclass
class _WorkflowState:
    analysis_run: AnalysisRun
    project: ThesisProject
    agents_by_slug: dict[str, Agent]
    agent_results: dict[str, AgentRunResult] = field(default_factory=dict)
    partial_failures: list[WorkflowAgentFailure] = field(default_factory=list)


def _default_agent_factories(llm_service: LLMService) -> dict[str, AgentFactory]:
    return {
        "literature-review": lambda record: LiteratureReviewAgent(**_agent_kwargs(record, llm_service)),
        "research-gap": lambda record: ResearchGapAgent(**_agent_kwargs(record, llm_service)),
        "citation": lambda record: CitationAgent(**_agent_kwargs(record, llm_service)),
        "methodology-consistency": lambda record: MethodologyConsistencyAgent(**_agent_kwargs(record, llm_service)),
        "results-interpretation": lambda record: ResultsInterpretationAgent(**_agent_kwargs(record, llm_service)),
        "defense-preparation": lambda record: DefensePreparationAgent(**_agent_kwargs(record, llm_service)),
        "report-generator": lambda record: ReportGeneratorAgent(**_agent_kwargs(record, llm_service)),
    }


def _agent_kwargs(record: Agent | None, llm_service: LLMService) -> dict[str, Any]:
    return {
        "llm_service": llm_service,
        "model": record.default_model_name if record else None,
        "provider": record.default_model_provider if record else None,
        "temperature": record.temperature if record else 0.2,
    }


def _load_analysis_run(db: Session, analysis_run_id: UUID) -> AnalysisRun:
    analysis_run = db.scalar(
        select(AnalysisRun)
        .options(selectinload(AnalysisRun.project))
        .where(AnalysisRun.id == analysis_run_id)
    )
    if analysis_run is None:
        raise ThesisReviewWorkflowError("Analysis run was not found.")
    return analysis_run


def _load_agents(db: Session) -> dict[str, Agent]:
    records = db.scalars(select(Agent).where(Agent.slug.in_(WORKFLOW_AGENT_SLUGS), Agent.is_active.is_(True))).all()
    return {record.slug: record for record in records}


def _load_document_chunks(db: Session, project_id: UUID) -> list[DocumentChunk]:
    return list(
        db.scalars(
            select(DocumentChunk)
            .join(DocumentChunk.document)
            .where(DocumentChunk.document.has(project_id=project_id))
            .order_by(DocumentChunk.created_at.asc(), DocumentChunk.chunk_index.asc())
        )
    )


def _load_references(db: Session, project_id: UUID) -> list[Reference]:
    return list(db.scalars(select(Reference).where(Reference.project_id == project_id).order_by(Reference.created_at.asc())))


def _load_csv_metadata(db: Session, project_id: UUID) -> dict[str, Any] | None:
    rows = db.execute(
        select(Document.filename, Document.parse_metadata)
        .where(Document.project_id == project_id, Document.document_type == "result_file", Document.parse_metadata.is_not(None))
        .order_by(Document.created_at.desc())
    ).all()
    if not rows:
        return None
    return {"files": [{"filename": filename, "metadata": metadata} for filename, metadata in rows]}


def _load_citation_checks(db: Session, analysis_run_id: UUID) -> list[CitationCheck]:
    return list(db.scalars(select(CitationCheck).where(CitationCheck.analysis_run_id == analysis_run_id).order_by(CitationCheck.created_at.asc())))


def _load_agent_messages(db: Session, analysis_run_id: UUID) -> list[AgentMessage]:
    return list(db.scalars(select(AgentMessage).where(AgentMessage.analysis_run_id == analysis_run_id).order_by(AgentMessage.created_at.asc())))


def _project_context(project: ThesisProject) -> dict[str, Any]:
    return {
        "id": str(project.id),
        "title": project.title,
        "research_area": project.research_area,
        "thesis_stage": project.thesis_stage,
        "status": project.status,
        "abstract": project.abstract,
        "problem_statement": project.problem_statement,
        "research_gap": project.research_gap,
        "objectives": project.objectives,
        "methodology_summary": project.methodology_summary,
        "dataset_summary": project.dataset_summary,
        "results_summary": project.results_summary,
    }


def _agent_id(state: _WorkflowState, slug: str) -> UUID | None:
    record = state.agents_by_slug.get(slug)
    return record.id if record else None


def _result_findings(state: _WorkflowState, slug: str) -> list[dict[str, Any]]:
    result = state.agent_results.get(slug)
    if result is None:
        return []
    return [finding.model_dump() for finding in result.findings]


def _all_result_findings(state: _WorkflowState) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for slug in WORKFLOW_AGENT_SLUGS:
        findings.extend(_result_findings(state, slug))
    return findings


def _defense_questions(state: _WorkflowState) -> list[dict[str, Any]]:
    result = state.agent_results.get("defense-preparation")
    if result is None:
        return []
    questions = result.raw_output.get("defense_questions") or []
    return [dict(question) for question in questions if isinstance(question, Mapping)]


def _handoff_summary(agent: Any, result: AgentRunResult) -> str:
    if hasattr(agent, "handoff_summary"):
        return str(agent.handoff_summary(result))
    return str(result.raw_output.get("handoff_summary") or f"{result.agent_name} completed.")


def _serialize_citation_checks(checks: Iterable[CitationCheck]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(check.id),
            "reference_id": str(check.reference_id) if check.reference_id else None,
            "claim_text": check.claim_text,
            "status": check.status,
            "confidence": check.confidence,
            "notes": check.notes,
        }
        for check in checks
    ]


def _serialize_agent_messages(messages: Iterable[AgentMessage]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(message.id),
            "from_agent_id": str(message.from_agent_id) if message.from_agent_id else None,
            "to_agent_id": str(message.to_agent_id) if message.to_agent_id else None,
            "message_type": message.message_type,
            "task": message.task,
            "summary": message.summary,
            "payload": message.payload,
            "status": message.status,
        }
        for message in messages
    ]


def _display_agent_name(slug: str) -> str:
    return slug.replace("-", " ").title()
