"""add agent_actions idempotency_key

Revision ID: 00834d18cde6
Revises: 942d3cb7420f
Create Date: 2026-02-09 20:08:55.215684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00834d18cde6'
down_revision: Union[str, None] = '942d3cb7420f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "agent_actions",
        sa.Column("idempotency_key", sa.String(length=64), nullable=True)
    )


def downgrade():
    op.drop_column("agent_actions", "idempotency_key")
