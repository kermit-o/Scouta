"""add idempotency_key to agent_actions

Revision ID: 8ca13e5f84af
Revises: 6b3db0fe7900
Create Date: 2026-02-08 17:26:28.665328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ca13e5f84af'
down_revision: Union[str, None] = '6b3db0fe7900'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "agent_actions",
        sa.Column("idempotency_key", sa.String(length=128), nullable=True)
    )
    op.create_index(
        "ix_agent_actions_idempotency_key",
        "agent_actions",
        ["idempotency_key"]
    )


def downgrade():
    op.drop_index("ix_agent_actions_idempotency_key", table_name="agent_actions")
    op.drop_column("agent_actions", "idempotency_key")
