"""add bibtex metadata fields to references

Revision ID: 20260617_0005
Revises: 20260617_0004
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260617_0005"
down_revision: str | None = "20260617_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("references", sa.Column("citation_key", sa.String(length=255), nullable=True))
    op.add_column("references", sa.Column("venue", sa.Text(), nullable=True))
    op.add_column("references", sa.Column("raw_bibtex", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("references", "raw_bibtex")
    op.drop_column("references", "venue")
    op.drop_column("references", "citation_key")
