\"\"\"unique agent_actions idempotency_key per org

Revision ID: idx_20260209_203538
Revises: 00834d18cde6
Create Date: 2026-02-09 20:35:38

\"\"\"
from alembic import op
import sqlalchemy as sa

revision = "idx_20260209_203538"
down_revision = "00834d18cde6"
branch_labels = None
depends_on = None


def _index_exists(conn, table: str, index_name: str) -> bool:
    insp = sa.inspect(conn)
    idx = insp.get_indexes(table)
    return any(i.get("name") == index_name for i in idx)


def upgrade() -> None:
    conn = op.get_bind()
    name = "uq_agent_actions_org_idempotency"
    if not _index_exists(conn, "agent_actions", name):
        op.create_index(
            name,
            "agent_actions",
            ["org_id", "idempotency_key"],
            unique=True,
        )


def downgrade() -> None:
    conn = op.get_bind()
    name = "uq_agent_actions_org_idempotency"
    if _index_exists(conn, "agent_actions", name):
        op.drop_index(name, table_name="agent_actions")
