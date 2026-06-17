"""add structured report and task fields

Revision ID: 20260617_0007
Revises: 20260617_0006
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260617_0007"
down_revision: str | None = "20260617_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

uuid_type = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.add_column("reports", sa.Column("overall_score", sa.Float(), nullable=True))
    op.add_column("reports", sa.Column("score_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("reports", sa.Column("executive_summary", sa.Text(), nullable=True))
    op.add_column("reports", sa.Column("structured_report", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.add_column("action_tasks", sa.Column("report_id", uuid_type, nullable=True))
    op.add_column("action_tasks", sa.Column("category", sa.String(length=100), nullable=True))
    op.add_column("action_tasks", sa.Column("priority", sa.String(length=50), server_default="medium", nullable=False))
    op.create_index("ix_action_tasks_report_id", "action_tasks", ["report_id"])
    op.create_foreign_key(
        "fk_action_tasks_report_id_reports",
        "action_tasks",
        "reports",
        ["report_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("action_tasks", "priority", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_action_tasks_report_id_reports", "action_tasks", type_="foreignkey")
    op.drop_index("ix_action_tasks_report_id", table_name="action_tasks")
    op.drop_column("action_tasks", "priority")
    op.drop_column("action_tasks", "category")
    op.drop_column("action_tasks", "report_id")

    op.drop_column("reports", "structured_report")
    op.drop_column("reports", "executive_summary")
    op.drop_column("reports", "score_breakdown")
    op.drop_column("reports", "overall_score")
