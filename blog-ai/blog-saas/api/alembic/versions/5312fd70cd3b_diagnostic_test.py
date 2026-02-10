"""diagnostic_test

Revision ID: 5312fd70cd3b
Revises: 8ca13e5f84af
Create Date: 2026-02-08 17:28:00.107894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5312fd70cd3b'
down_revision: Union[str, None] = '8ca13e5f84af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
