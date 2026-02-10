"""add idempotency_key to agent_actions (forward)

Revision ID: 942d3cb7420f
Revises: 5312fd70cd3b
Create Date: 2026-02-08 17:33:25.781859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '942d3cb7420f'
down_revision: Union[str, None] = '5312fd70cd3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
