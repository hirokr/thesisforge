"""add document text parsing fields

Revision ID: 20260617_0004
Revises: 20260617_0003
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260617_0004"
down_revision: str | None = "20260617_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("raw_text", sa.Text(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("parse_status", sa.String(length=50), nullable=False, server_default="pending"),
    )
    op.alter_column("documents", "parse_status", server_default=None)


def downgrade() -> None:
    op.drop_column("documents", "parse_status")
    op.drop_column("documents", "raw_text")
