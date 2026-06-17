"""add document parse metadata

Revision ID: 20260617_0006
Revises: 20260617_0005
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260617_0006"
down_revision: str | None = "20260617_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("parse_metadata", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "parse_metadata")
