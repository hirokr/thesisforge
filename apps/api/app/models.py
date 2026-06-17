from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    auth_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="researcher", nullable=False)
    institution: Mapped[str | None] = mapped_column(String(255))

    projects: Mapped[list["ThesisProject"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class ThesisProject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "thesis_projects"

    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    research_area: Mapped[str | None] = mapped_column(String(255))
    thesis_stage: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    latest_score: Mapped[float | None] = mapped_column(Float)
    abstract: Mapped[str | None] = mapped_column(Text)
    problem_statement: Mapped[str | None] = mapped_column(Text)
    research_gap: Mapped[str | None] = mapped_column(Text)
    objectives: Mapped[str | None] = mapped_column(Text)
    methodology_summary: Mapped[str | None] = mapped_column(Text)
    dataset_summary: Mapped[str | None] = mapped_column(Text)
    results_summary: Mapped[str | None] = mapped_column(Text)

    owner: Mapped["UserProfile"] = relationship(back_populates="projects")
    documents: Mapped[list["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    analysis_runs: Mapped[list["AnalysisRun"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    action_tasks: Mapped[list["ActionTask"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    supervisor_feedback: Mapped[list["SupervisorFeedback"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    agent_messages: Mapped[list["AgentMessage"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(1024))
    content_type: Mapped[str | None] = mapped_column(String(120))
    document_type: Mapped[str] = mapped_column(String(80), default="thesis_draft", nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text)
    parse_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    parse_metadata: Mapped[dict | None] = mapped_column(JSON)

    project: Mapped["ThesisProject"] = relationship(back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    references: Mapped[list["Reference"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_document_index"),)

    document_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_start: Mapped[int | None] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer)
    embedding_id: Mapped[str | None] = mapped_column(String(255))

    document: Mapped["Document"] = relationship(back_populates="chunks")


class Reference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "references"

    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    document_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    citation_key: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(Text)
    authors: Mapped[list[str] | None] = mapped_column(JSON)
    year: Mapped[int | None] = mapped_column(Integer)
    venue: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(Text)
    citation_text: Mapped[str | None] = mapped_column(Text)
    raw_bibtex: Mapped[str | None] = mapped_column(Text)

    project: Mapped["ThesisProject"] = relationship()
    document: Mapped["Document"] = relationship(back_populates="references")
    citation_checks: Mapped[list["CitationCheck"]] = relationship(back_populates="reference", cascade="all, delete-orphan")


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    default_model_provider: Mapped[str] = mapped_column(String(80), nullable=False)
    default_model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    messages: Mapped[list["AgentMessage"]] = relationship(back_populates="agent", foreign_keys="AgentMessage.agent_id")
    findings: Mapped[list["AgentFinding"]] = relationship(back_populates="agent")


class AnalysisRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "analysis_runs"

    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)
    overall_score: Mapped[float | None] = mapped_column(Float)

    project: Mapped["ThesisProject"] = relationship(back_populates="analysis_runs")
    messages: Mapped[list["AgentMessage"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    findings: Mapped[list["AgentFinding"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    citation_checks: Mapped[list["CitationCheck"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="analysis_run")


class AgentMessage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_messages"

    analysis_run_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), index=True)
    from_agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), index=True)
    to_agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(80), default="handoff", nullable=False)
    task: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSON)
    band_message_id: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSON)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="messages")
    project: Mapped["ThesisProject"] = relationship(back_populates="agent_messages")
    agent: Mapped["Agent"] = relationship(back_populates="messages", foreign_keys=[agent_id])
    from_agent: Mapped["Agent | None"] = relationship(foreign_keys=[from_agent_id])
    to_agent: Mapped["Agent | None"] = relationship(foreign_keys=[to_agent_id])


class AgentFinding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_findings"

    analysis_run_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict | None] = mapped_column(JSON)
    recommendation: Mapped[str | None] = mapped_column(Text)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="findings")
    agent: Mapped["Agent"] = relationship(back_populates="findings")


class CitationCheck(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "citation_checks"

    analysis_run_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    reference_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("references.id", ondelete="SET NULL"), index=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="citation_checks")
    reference: Mapped["Reference"] = relationship(back_populates="citation_checks")


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    analysis_run_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("analysis_runs.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    overall_score: Mapped[float | None] = mapped_column(Float)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON)
    executive_summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    structured_report: Mapped[dict | None] = mapped_column(JSON)
    export_path: Mapped[str | None] = mapped_column(String(1024))

    project: Mapped["ThesisProject"] = relationship(back_populates="reports")
    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="reports")
    action_tasks: Mapped[list["ActionTask"]] = relationship(back_populates="report")


class ActionTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "action_tasks"

    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    report_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reports.id", ondelete="SET NULL"), index=True)
    finding_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agent_findings.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped["ThesisProject"] = relationship(back_populates="action_tasks")
    report: Mapped["Report"] = relationship(back_populates="action_tasks")
    finding: Mapped["AgentFinding"] = relationship()


class SupervisorFeedback(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "supervisor_feedback"

    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(80), default="manual", nullable=False)
    feedback_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)

    project: Mapped["ThesisProject"] = relationship(back_populates="supervisor_feedback")


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"

    project_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("thesis_projects.id", ondelete="CASCADE"), index=True)
    actor_user_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("user_profiles.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    details: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped["ThesisProject"] = relationship(back_populates="audit_logs")
    actor: Mapped["UserProfile"] = relationship()
