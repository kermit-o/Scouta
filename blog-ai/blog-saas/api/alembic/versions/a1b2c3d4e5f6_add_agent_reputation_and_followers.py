"""add agent reputation and followers

Revision ID: a1b2c3d4e5f6
Revises: 8500f153f80f
Create Date: 2026-03-01 04:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8500f153f80f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()

    # 1. Columnas en agent_profiles (IF NOT EXISTS)
    cols = {
        'reputation_score': 'INTEGER DEFAULT 0 NOT NULL',
        'total_comments': 'INTEGER DEFAULT 0 NOT NULL',
        'total_upvotes': 'INTEGER DEFAULT 0 NOT NULL',
        'total_downvotes': 'INTEGER DEFAULT 0 NOT NULL',
        'follower_count': 'INTEGER DEFAULT 0 NOT NULL',
        'bio': 'TEXT',
        'is_public': 'BOOLEAN DEFAULT true NOT NULL',
    }
    for col, typedef in cols.items():
        try:
            conn.execute(text(f"ALTER TABLE agent_profiles ADD COLUMN IF NOT EXISTS {col} {typedef}"))
        except Exception as e:
            print(f"SKIP {col}: {e}")

    # 2. Crear agent_followers si no existe
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS agent_followers (
            id SERIAL NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            agent_id INTEGER NOT NULL REFERENCES agent_profiles(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT uq_agent_followers_user_agent UNIQUE (user_id, agent_id)
        )
    """))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_agent_followers_agent_id ON agent_followers (agent_id)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_agent_followers_user_id ON agent_followers (user_id)"))

def downgrade() -> None:
    op.drop_table('agent_followers')
    with op.batch_alter_table('agent_profiles') as batch_op:
        for col in ['reputation_score', 'total_comments', 'total_upvotes', 'total_downvotes', 'follower_count', 'bio', 'is_public']:
            batch_op.drop_column(col)
