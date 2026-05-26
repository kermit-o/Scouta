"""add users.deleted_at (account soft-delete) + merge open heads

Adds the nullable users.deleted_at column used for store-compliant account
deletion. Also acts as a MERGE migration: the revision graph had three open
heads (live recordings, posts media, private-room live fields); this revision
descends from all three so `alembic upgrade head` resolves to a single head.

Idempotent — guarded by inspect() so re-running is safe.

Revision ID: m20260526_user_deleted_at
Revises: m20260524_live_recordings, f5250ae8b247, a1c2e3f4g5h6
Create Date: 2026-05-26
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "m20260526_user_deleted_at"
down_revision = ("m20260524_live_recordings", "f5250ae8b247", "a1c2e3f4g5h6")
branch_labels = None
depends_on = None


def _has_column(conn, table: str, column: str) -> bool:
    try:
        return any(c["name"] == column for c in inspect(conn).get_columns(table))
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_column(conn, "users", "deleted_at"):
        op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    if _has_column(conn, "users", "deleted_at"):
        op.drop_column("users", "deleted_at")
