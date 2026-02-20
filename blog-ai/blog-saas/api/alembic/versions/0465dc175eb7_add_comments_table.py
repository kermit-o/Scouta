"""add comments table

Revision ID: 0465dc175eb7
Revises: idx_20260216160459_uq_posts_org_content_hash
Create Date: 2026-02-17 20:09:59.857771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0465dc175eb7'
down_revision: Union[str, None] = 'idx_20260216160459_uq_posts_org_content_hash'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
