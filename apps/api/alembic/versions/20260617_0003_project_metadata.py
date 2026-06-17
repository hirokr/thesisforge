"""add thesis project metadata fields

Revision ID: 20260617_0003
Revises: 20260617_0002
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260617_0003"
down_revision: str | None = "20260617_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PROJECT_METADATA_COLUMNS = [
    "problem_statement",
    "research_gap",
    "objectives",
    "methodology_summary",
    "dataset_summary",
    "results_summary",
]


def upgrade() -> None:
    for column_name in PROJECT_METADATA_COLUMNS:
        op.add_column("thesis_projects", sa.Column(column_name, sa.Text(), nullable=True))


def downgrade() -> None:
    for column_name in reversed(PROJECT_METADATA_COLUMNS):
        op.drop_column("thesis_projects", column_name)
