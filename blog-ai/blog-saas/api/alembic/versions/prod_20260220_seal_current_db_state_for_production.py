"""seal current db state for production

Revision ID: prod_20260220
Revises: prod_20260220
Create Date: 2026-02-20 01:47:31.262562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'prod_20260220'
down_revision: Union[str, None] = '0465dc175eb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Estado actual sellado — schema sincronizado manualmente
    pass


def downgrade() -> None:
    pass
