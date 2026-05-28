"""add agent_actions idempotency_key

Revision ID: 00834d18cde6
Revises: 942d3cb7420f
Create Date: 2026-02-09 20:08:55.215684

Hardened to be idempotent: only adds the column if `agent_actions` exists and
the column is not already present (some environments build the schema from the
SQLAlchemy models via create_all, which leaves the column already in place).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '00834d18cde6'
down_revision: Union[str, None] = '942d3cb7420f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(conn, table: str) -> bool:
    try:
        return table in inspect(conn).get_table_names()
    except Exception:
        return False


def _has_column(conn, table: str, column: str) -> bool:
    try:
        return any(c["name"] == column for c in inspect(conn).get_columns(table))
    except Exception:
        return False


def upgrade():
    conn = op.get_bind()
    if _has_table(conn, "agent_actions") and not _has_column(conn, "agent_actions", "idempotency_key"):
        op.add_column(
            "agent_actions",
            sa.Column("idempotency_key", sa.String(length=64), nullable=True),
        )


def downgrade():
    conn = op.get_bind()
    if _has_column(conn, "agent_actions", "idempotency_key"):
        op.drop_column("agent_actions", "idempotency_key")
