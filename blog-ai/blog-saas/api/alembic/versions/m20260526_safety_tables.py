"""trust & safety tables: reports + user_blocks

Adds the UGC reporting (`reports`) and account-level block (`user_blocks`)
tables required for App Store / Google Play UGC moderation.

Idempotent — guarded by inspect() so re-running is safe.

Revision ID: m20260526_safety_tables
Revises: m20260526_user_deleted_at
Create Date: 2026-05-26
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "m20260526_safety_tables"
down_revision = "m20260526_user_deleted_at"
branch_labels = None
depends_on = None


def _has_table(conn, table: str) -> bool:
    try:
        return table in inspect(conn).get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()

    if not _has_table(conn, "reports"):
        op.create_table(
            "reports",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("reporter_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("target_type", sa.String(length=20), nullable=False),
            sa.Column("target_id", sa.String(length=100), nullable=False),
            sa.Column("reason", sa.String(length=50), nullable=False),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_reports_status", "reports", ["status"])

    if not _has_table(conn, "user_blocks"):
        op.create_table(
            "user_blocks",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("blocker_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("blocked_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint("blocker_user_id", "blocked_user_id", name="uq_user_block"),
        )


def downgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "user_blocks"):
        op.drop_table("user_blocks")
    if _has_table(conn, "reports"):
        op.drop_index("ix_reports_status", table_name="reports")
        op.drop_table("reports")
