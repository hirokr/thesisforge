"""add workflow fields to agent messages

Revision ID: 20260617_0008
Revises: 20260617_0007
Create Date: 2026-06-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260617_0008"
down_revision: str | None = "20260617_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    op.add_column("agent_messages", sa.Column("project_id", uuid_type, nullable=True))
    op.add_column("agent_messages", sa.Column("from_agent_id", uuid_type, nullable=True))
    op.add_column("agent_messages", sa.Column("to_agent_id", uuid_type, nullable=True))
    op.add_column("agent_messages", sa.Column("message_type", sa.String(length=80), server_default="handoff", nullable=False))
    op.add_column("agent_messages", sa.Column("task", sa.String(length=255), nullable=True))
    op.add_column("agent_messages", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("agent_messages", sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("agent_messages", sa.Column("band_message_id", sa.String(length=255), nullable=True))
    op.add_column("agent_messages", sa.Column("status", sa.String(length=50), server_default="pending", nullable=False))
    op.create_foreign_key(
        "fk_agent_messages_project_id_thesis_projects",
        "agent_messages",
        "thesis_projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_agent_messages_from_agent_id_agents",
        "agent_messages",
        "agents",
        ["from_agent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_agent_messages_to_agent_id_agents",
        "agent_messages",
        "agents",
        ["to_agent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_agent_messages_project_id", "agent_messages", ["project_id"])
    op.create_index("ix_agent_messages_from_agent_id", "agent_messages", ["from_agent_id"])
    op.create_index("ix_agent_messages_to_agent_id", "agent_messages", ["to_agent_id"])
    op.create_index("ix_agent_messages_band_message_id", "agent_messages", ["band_message_id"])


def downgrade() -> None:
    op.drop_index("ix_agent_messages_band_message_id", table_name="agent_messages")
    op.drop_index("ix_agent_messages_to_agent_id", table_name="agent_messages")
    op.drop_index("ix_agent_messages_from_agent_id", table_name="agent_messages")
    op.drop_index("ix_agent_messages_project_id", table_name="agent_messages")
    op.drop_constraint("fk_agent_messages_to_agent_id_agents", "agent_messages", type_="foreignkey")
    op.drop_constraint("fk_agent_messages_from_agent_id_agents", "agent_messages", type_="foreignkey")
    op.drop_constraint("fk_agent_messages_project_id_thesis_projects", "agent_messages", type_="foreignkey")
    op.drop_column("agent_messages", "status")
    op.drop_column("agent_messages", "band_message_id")
    op.drop_column("agent_messages", "payload")
    op.drop_column("agent_messages", "summary")
    op.drop_column("agent_messages", "task")
    op.drop_column("agent_messages", "message_type")
    op.drop_column("agent_messages", "to_agent_id")
    op.drop_column("agent_messages", "from_agent_id")
    op.drop_column("agent_messages", "project_id")
