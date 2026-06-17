"""create initial thesisforge schema

Revision ID: 20260617_0001
Revises:
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260617_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

uuid_type = postgresql.UUID(as_uuid=True)
uuid_default = sa.text("gen_random_uuid()")


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "user_profiles",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("auth_user_id", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=True),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("auth_user_id"),
    )
    op.create_index("ix_user_profiles_auth_user_id", "user_profiles", ["auth_user_id"])

    op.create_table(
        "agents",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("default_model_provider", sa.String(length=80), nullable=False),
        sa.Column("default_model_name", sa.String(length=120), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_agents_slug", "agents", ["slug"])

    op.create_table(
        "thesis_projects",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("owner_id", uuid_type, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("research_area", sa.String(length=255), nullable=True),
        sa.Column("thesis_stage", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("latest_score", sa.Float(), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["owner_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_thesis_projects_owner_id", "thesis_projects", ["owner_id"])

    op.create_table(
        "documents",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=True),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_project_id", "documents", ["project_id"])

    op.create_table(
        "analysis_runs",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_runs_project_id", "analysis_runs", ["project_id"])

    op.create_table(
        "references",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=False),
        sa.Column("document_id", uuid_type, nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("authors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("doi", sa.String(length=255), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("citation_text", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_references_document_id", "references", ["document_id"])
    op.create_index("ix_references_project_id", "references", ["project_id"])

    op.create_table(
        "document_chunks",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("document_id", uuid_type, nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("embedding_id", sa.String(length=255), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_document_index"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])

    op.create_table(
        "agent_messages",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("analysis_run_id", uuid_type, nullable=False),
        sa.Column("agent_id", uuid_type, nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_messages_agent_id", "agent_messages", ["agent_id"])
    op.create_index("ix_agent_messages_analysis_run_id", "agent_messages", ["analysis_run_id"])

    op.create_table(
        "agent_findings",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("analysis_run_id", uuid_type, nullable=False),
        sa.Column("agent_id", uuid_type, nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_findings_agent_id", "agent_findings", ["agent_id"])
    op.create_index("ix_agent_findings_analysis_run_id", "agent_findings", ["analysis_run_id"])

    op.create_table(
        "citation_checks",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("analysis_run_id", uuid_type, nullable=False),
        sa.Column("reference_id", uuid_type, nullable=True),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reference_id"], ["references.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_citation_checks_analysis_run_id", "citation_checks", ["analysis_run_id"])
    op.create_index("ix_citation_checks_reference_id", "citation_checks", ["reference_id"])

    op.create_table(
        "reports",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=False),
        sa.Column("analysis_run_id", uuid_type, nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("export_path", sa.String(length=1024), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reports_analysis_run_id", "reports", ["analysis_run_id"])
    op.create_index("ix_reports_project_id", "reports", ["project_id"])

    op.create_table(
        "action_tasks",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=False),
        sa.Column("finding_id", uuid_type, nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["finding_id"], ["agent_findings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_action_tasks_finding_id", "action_tasks", ["finding_id"])
    op.create_index("ix_action_tasks_project_id", "action_tasks", ["project_id"])

    op.create_table(
        "supervisor_feedback",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_supervisor_feedback_project_id", "supervisor_feedback", ["project_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", uuid_type, server_default=uuid_default, nullable=False),
        sa.Column("project_id", uuid_type, nullable=True),
        sa.Column("actor_user_id", uuid_type, nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", uuid_type, nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["user_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["thesis_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_project_id", "audit_logs", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_project_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_supervisor_feedback_project_id", table_name="supervisor_feedback")
    op.drop_table("supervisor_feedback")
    op.drop_index("ix_action_tasks_project_id", table_name="action_tasks")
    op.drop_index("ix_action_tasks_finding_id", table_name="action_tasks")
    op.drop_table("action_tasks")
    op.drop_index("ix_reports_project_id", table_name="reports")
    op.drop_index("ix_reports_analysis_run_id", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_citation_checks_reference_id", table_name="citation_checks")
    op.drop_index("ix_citation_checks_analysis_run_id", table_name="citation_checks")
    op.drop_table("citation_checks")
    op.drop_index("ix_agent_findings_analysis_run_id", table_name="agent_findings")
    op.drop_index("ix_agent_findings_agent_id", table_name="agent_findings")
    op.drop_table("agent_findings")
    op.drop_index("ix_agent_messages_analysis_run_id", table_name="agent_messages")
    op.drop_index("ix_agent_messages_agent_id", table_name="agent_messages")
    op.drop_table("agent_messages")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_references_project_id", table_name="references")
    op.drop_index("ix_references_document_id", table_name="references")
    op.drop_table("references")
    op.drop_index("ix_analysis_runs_project_id", table_name="analysis_runs")
    op.drop_table("analysis_runs")
    op.drop_index("ix_documents_project_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_thesis_projects_owner_id", table_name="thesis_projects")
    op.drop_table("thesis_projects")
    op.drop_index("ix_agents_slug", table_name="agents")
    op.drop_table("agents")
    op.drop_index("ix_user_profiles_auth_user_id", table_name="user_profiles")
    op.drop_table("user_profiles")
