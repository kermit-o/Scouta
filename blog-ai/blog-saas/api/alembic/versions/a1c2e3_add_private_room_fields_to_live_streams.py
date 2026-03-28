"""add_private_room_fields_to_live_streams

Revision ID: a1c2e3f4g5h6
Revises: 8500f153f80f
Create Date: 2026-03-28 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1c2e3f4g5h6'
down_revision: Union[str, None] = '8500f153f80f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add private room columns to live_streams
    with op.batch_alter_table('live_streams') as batch_op:
        batch_op.add_column(sa.Column('is_private', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('access_type', sa.String(length=20), nullable=True, server_default='public'))
        batch_op.add_column(sa.Column('entry_coin_cost', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('max_viewer_limit', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    with op.batch_alter_table('live_streams') as batch_op:
        batch_op.drop_column('max_viewer_limit')
        batch_op.drop_column('entry_coin_cost')
        batch_op.drop_column('access_type')
        batch_op.drop_column('password_hash')
        batch_op.drop_column('is_private')
