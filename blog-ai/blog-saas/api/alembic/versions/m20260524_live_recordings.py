"""live_recordings table (VOD / replay)

Stores LiveKit Egress recording metadata. Idempotent — guarded by inspect().

Revision ID: m20260524_live_recordings
Revises: m20260524_live_realtime
Create Date: 2026-05-24
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "m20260524_live_recordings"
down_revision = "m20260524_live_realtime"
branch_labels = None
depends_on = None


def _has_table(conn, table: str) -> bool:
    try:
        return table in inspect(conn).get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "live_recordings"):
        return
    op.create_table(
        "live_recordings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("room_name", sa.String(length=100), nullable=False),
        sa.Column("host_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("egress_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="recording"),
        sa.Column("file_key", sa.String(length=255), nullable=True),
        sa.Column("playback_url", sa.String(length=500), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_live_recordings_room_name", "live_recordings", ["room_name"])
    op.create_index("ix_live_recordings_host_user_id", "live_recordings", ["host_user_id"])
    op.create_index("ix_live_recordings_egress_id", "live_recordings", ["egress_id"])
    op.create_index("ix_live_recordings_host_status", "live_recordings", ["host_user_id", "status"])


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "live_recordings"):
        return
    for idx in (
        "ix_live_recordings_host_status",
        "ix_live_recordings_egress_id",
        "ix_live_recordings_host_user_id",
        "ix_live_recordings_room_name",
    ):
        op.drop_index(idx, table_name="live_recordings")
    op.drop_table("live_recordings")
