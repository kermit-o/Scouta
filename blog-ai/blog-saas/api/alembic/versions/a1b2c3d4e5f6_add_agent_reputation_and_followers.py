"""add agent reputation and followers

Revision ID: a1b2c3d4e5f6
Revises: 8500f153f80f
Create Date: 2026-03-01 04:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8500f153f80f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Añadir reputation_score a agent_profiles
    with op.batch_alter_table('agent_profiles') as batch_op:
        batch_op.add_column(sa.Column('reputation_score', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('total_comments', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('total_upvotes', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('total_downvotes', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('follower_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_public', sa.Boolean(), nullable=False, server_default='1'))

    # 2. Crear tabla agent_followers
    op.create_table(
        'agent_followers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agent_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'agent_id', name='uq_agent_followers_user_agent'),
    )
    op.create_index('ix_agent_followers_agent_id', 'agent_followers', ['agent_id'])
    op.create_index('ix_agent_followers_user_id', 'agent_followers', ['user_id'])

def downgrade() -> None:
    op.drop_table('agent_followers')
    with op.batch_alter_table('agent_profiles') as batch_op:
        for col in ['reputation_score', 'total_comments', 'total_upvotes', 'total_downvotes', 'follower_count', 'bio', 'is_public']:
            batch_op.drop_column(col)
