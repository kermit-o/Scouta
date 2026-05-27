"""create user_events table for product analytics

Append-only event log: one row per significant user action. Idempotent —
guarded by inspect() so re-runs and environments where the table was
auto-created (Base.metadata.create_all) are no-ops.

Revision ID: m20260504_user_events
Revises: m20260504_baseline_drift
Create Date: 2026-05-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "m20260504_user_events"
down_revision = "m20260504_baseline_drift"
branch_labels = None
depends_on = None


def _has_table(conn, table: str) -> bool:
    try:
        return table in inspect(conn).get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "user_events"):
        return

    op.create_table(
        "user_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("properties", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_events_user_id", "user_events", ["user_id"])
    op.create_index("ix_user_events_event_type", "user_events", ["event_type"])
    op.create_index("ix_user_events_created_at", "user_events", ["created_at"])
    op.create_index("ix_user_events_type_created", "user_events", ["event_type", "created_at"])


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "user_events"):
        return
    op.drop_index("ix_user_events_type_created", table_name="user_events")
    op.drop_index("ix_user_events_created_at", table_name="user_events")
    op.drop_index("ix_user_events_event_type", table_name="user_events")
    op.drop_index("ix_user_events_user_id", table_name="user_events")
    op.drop_table("user_events")
