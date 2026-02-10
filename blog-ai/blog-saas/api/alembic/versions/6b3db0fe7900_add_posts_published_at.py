"""add posts published_at

Revision ID: 6b3db0fe7900
Revises: d9e2dd518d28
Create Date: 2026-02-07 16:28:41.248689

"""
from alembic import op
import sqlalchemy as sa

revision = "6b3db0fe7900"
down_revision = "d9e2dd518d28"
branch_labels = None
depends_on = None


def _has_column(conn, table: str, col: str) -> bool:
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns(table)}
    return col in cols


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_column(conn, 'posts', 'published_at'):
        op.add_column('posts', sa.Column('published_at', sa.DateTime(), nullable=True))

def downgrade() -> None:
    conn = op.get_bind()
    if _has_column(conn, 'posts', 'published_at'):
        op.drop_column('posts', 'published_at')

