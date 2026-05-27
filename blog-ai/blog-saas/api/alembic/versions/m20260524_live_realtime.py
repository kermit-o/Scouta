"""durable live realtime: live_blocks + live_join_requests

Moves chat blocks and co-host join requests out of in-memory dicts (lost on
every restart) into Postgres. Idempotent — guarded by inspect().

Revision ID: m20260524_live_realtime
Revises: m20260504_user_events
Create Date: 2026-05-24
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "m20260524_live_realtime"
down_revision = "m20260504_user_events"
branch_labels = None
depends_on = None


def _has_table(conn, table: str) -> bool:
    try:
        return table in inspect(conn).get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()

    if not _has_table(conn, "live_blocks"):
        op.create_table(
            "live_blocks",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("room_name", sa.String(length=100), nullable=False),
            sa.Column("username", sa.String(length=150), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("room_name", "username", name="uq_live_block_room_user"),
        )
        op.create_index("ix_live_blocks_room_name", "live_blocks", ["room_name"])

    if not _has_table(conn, "live_join_requests"):
        op.create_table(
            "live_join_requests",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("room_name", sa.String(length=100), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("username", sa.String(length=150), nullable=False),
            sa.Column("display_name", sa.String(length=150), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("room_name", "user_id", name="uq_live_join_req_room_user"),
        )
        op.create_index("ix_live_join_requests_room_name", "live_join_requests", ["room_name"])


def downgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "live_join_requests"):
        op.drop_index("ix_live_join_requests_room_name", table_name="live_join_requests")
        op.drop_table("live_join_requests")
    if _has_table(conn, "live_blocks"):
        op.drop_index("ix_live_blocks_room_name", table_name="live_blocks")
        op.drop_table("live_blocks")
