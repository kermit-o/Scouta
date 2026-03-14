"""merge_media_columns

Revision ID: 983c49a8265d
Revises: a1b2c3d4e5f6, f5250ae8b247
Create Date: 2026-03-14 02:17:52.422312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '983c49a8265d'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'f5250ae8b247')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
