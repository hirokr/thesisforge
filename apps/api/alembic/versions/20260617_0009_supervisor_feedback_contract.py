"""align supervisor feedback fields with API contract

Revision ID: 20260617_0009
Revises: 20260617_0008
Create Date: 2026-06-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260617_0009"
down_revision: str | None = "20260617_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("supervisor_feedback", sa.Column("feedback_text", sa.Text(), nullable=True))
    op.add_column("supervisor_feedback", sa.Column("source", sa.String(length=80), server_default="manual", nullable=False))
    op.add_column("supervisor_feedback", sa.Column("feedback_date", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE supervisor_feedback SET feedback_text = content WHERE feedback_text IS NULL")
    op.alter_column("supervisor_feedback", "feedback_text", nullable=False)
    op.drop_column("supervisor_feedback", "author_name")
    op.drop_column("supervisor_feedback", "content")


def downgrade() -> None:
    op.add_column("supervisor_feedback", sa.Column("content", sa.Text(), nullable=True))
    op.add_column("supervisor_feedback", sa.Column("author_name", sa.String(length=255), nullable=True))
    op.execute("UPDATE supervisor_feedback SET content = feedback_text WHERE content IS NULL")
    op.alter_column("supervisor_feedback", "content", nullable=False)
    op.drop_column("supervisor_feedback", "feedback_date")
    op.drop_column("supervisor_feedback", "source")
    op.drop_column("supervisor_feedback", "feedback_text")
