"""add_private_room_fields_to_live_streams

Revision ID: a1c2e3f4g5h6
Revises: 8500f153f80f
Create Date: 2026-03-28 12:00:00.000000

Hardened to be idempotent and drift-tolerant: skips cleanly if `live_streams`
doesn't exist (in some environments tables are created from the SQLAlchemy
models via create_all, not alembic) and only adds columns that are missing.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = 'a1c2e3f4g5h6'
down_revision: Union[str, None] = '8500f153f80f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(conn, table):
    """Set of column names, or None if the table doesn't exist."""
    try:
        insp = inspect(conn)
        if table not in insp.get_table_names():
            return None
        return {c["name"] for c in insp.get_columns(table)}
    except Exception:
        return None


def upgrade() -> None:
    conn = op.get_bind()
    existing = _columns(conn, 'live_streams')
    if existing is None:
        return  # table built elsewhere (create_all); nothing to alter

    targets = [
        ('is_private', lambda: sa.Column('is_private', sa.Boolean(), nullable=True, server_default='false')),
        ('password_hash', lambda: sa.Column('password_hash', sa.String(length=255), nullable=True)),
        ('access_type', lambda: sa.Column('access_type', sa.String(length=20), nullable=True, server_default='public')),
        ('entry_coin_cost', lambda: sa.Column('entry_coin_cost', sa.Integer(), nullable=True, server_default='0')),
        ('max_viewer_limit', lambda: sa.Column('max_viewer_limit', sa.Integer(), nullable=True, server_default='0')),
    ]
    to_add = [make() for (name, make) in targets if name not in existing]
    if not to_add:
        return
    with op.batch_alter_table('live_streams') as batch_op:
        for col in to_add:
            batch_op.add_column(col)


def downgrade() -> None:
    conn = op.get_bind()
    existing = _columns(conn, 'live_streams')
    if existing is None:
        return
    with op.batch_alter_table('live_streams') as batch_op:
        for name in ['max_viewer_limit', 'entry_coin_cost', 'access_type', 'password_hash', 'is_private']:
            if name in existing:
                batch_op.drop_column(name)
