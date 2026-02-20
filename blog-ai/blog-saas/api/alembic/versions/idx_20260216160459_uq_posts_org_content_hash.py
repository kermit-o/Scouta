from alembic import op
from sqlalchemy import inspect

revision = "idx_20260216160459_uq_posts_org_content_hash"
down_revision = "idx_20260216155259_unique_posts_org_content_hash"
branch_labels = None
depends_on = None

TABLE = "posts"
INDEX = "uq_posts_org_content_hash"

def _index_exists(conn, name: str) -> bool:
    insp = inspect(conn)
    for ix in insp.get_indexes(TABLE):
        if ix.get("name") == name:
            return True
    return False

def upgrade():
    conn = op.get_bind()
    if not _index_exists(conn, INDEX):
        op.create_index(INDEX, TABLE, ["org_id", "content_hash"], unique=True)

def downgrade():
    conn = op.get_bind()
    if _index_exists(conn, INDEX):
        op.drop_index(INDEX, table_name=TABLE)
