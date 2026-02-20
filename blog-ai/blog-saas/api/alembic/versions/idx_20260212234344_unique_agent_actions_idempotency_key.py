from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "idx_20260212234344_unique_agent_actions_idempotency_key"
down_revision = "00834d18cde6"
branch_labels = None
depends_on = None

INDEX_NAME = "uq_agent_actions_idempotency_key"
TABLE_NAME = "agent_actions"
COLUMN_NAME = "idempotency_key"

def _index_exists(conn, name: str) -> bool:
    insp = inspect(conn)
    for ix in insp.get_indexes(TABLE_NAME):
        if ix.get("name") == name:
            return True
    return False

def upgrade():
    conn = op.get_bind()
    if not _index_exists(conn, INDEX_NAME):
        op.create_index(
            INDEX_NAME,
            TABLE_NAME,
            [COLUMN_NAME],
            unique=True
        )

def downgrade():
    conn = op.get_bind()
    if _index_exists(conn, INDEX_NAME):
        op.drop_index(INDEX_NAME, table_name=TABLE_NAME)
