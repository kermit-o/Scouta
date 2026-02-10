"""agent_policy_thresholds_and_shadowban

Revision ID: d9e2dd518d28
Revises: d9fbf3ad2165
Create Date: 2026-02-04 22:34:02.806021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9e2dd518d28'
down_revision: Union[str, None] = 'd9fbf3ad2165'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(conn, table: str, col: str) -> bool:
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns(table)}
    return col in cols


def upgrade() -> None:
    conn = op.get_bind()

    # agent_policies
    if not _has_column(conn, "agent_policies", "auto_approve_threshold"):
        op.add_column(
            "agent_policies",
            sa.Column("auto_approve_threshold", sa.Integer(), nullable=False, server_default="0"),
        )
    if not _has_column(conn, "agent_policies", "auto_reject_threshold"):
        op.add_column(
            "agent_policies",
            sa.Column("auto_reject_threshold", sa.Integer(), nullable=False, server_default="0"),
        )
    if not _has_column(conn, "agent_policies", "enable_llm_moderation"):
        op.add_column(
            "agent_policies",
            sa.Column("enable_llm_moderation", sa.Boolean(), nullable=False, server_default="0"),
        )

    # agent_profiles
    if not _has_column(conn, "agent_profiles", "is_shadow_banned"):
        op.add_column(
            "agent_profiles",
            sa.Column("is_shadow_banned", sa.Boolean(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    conn = op.get_bind()

    with op.batch_alter_table("agent_profiles") as b:
        if _has_column(conn, "agent_profiles", "is_shadow_banned"):
            b.drop_column("is_shadow_banned")

    with op.batch_alter_table("agent_policies") as b:
        if _has_column(conn, "agent_policies", "enable_llm_moderation"):
            b.drop_column("enable_llm_moderation")
        if _has_column(conn, "agent_policies", "auto_reject_threshold"):
            b.drop_column("auto_reject_threshold")
        if _has_column(conn, "agent_policies", "auto_approve_threshold"):
            b.drop_column("auto_approve_threshold")