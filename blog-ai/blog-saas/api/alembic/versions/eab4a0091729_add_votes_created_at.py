"""add votes.created_at

Revision ID: eab4a0091729
Revises: prod_20260220
Create Date: 2026-02-21 13:09:05.849907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eab4a0091729'
down_revision: Union[str, None] = 'prod_20260220'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "votes",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("votes", "created_at")