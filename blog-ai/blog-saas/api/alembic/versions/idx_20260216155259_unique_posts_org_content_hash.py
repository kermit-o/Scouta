from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "idx_20260216155259_unique_posts_org_content_hash"
down_revision = "idx_20260216011217_posts_content_hash_unique"
branch_labels = None
depends_on = None

TABLE = "posts"
COL = "content_hash"
IX = "uq_posts_org_content_hash"

def _has_column(conn) -> bool:
    insp = inspect(conn)
    cols = [c["name"] for c in insp.get_columns(TABLE)]
    return COL in cols

def _has_index(conn) -> bool:
    insp = inspect(conn)
    for ix in insp.get_indexes(TABLE):
        if ix.get("name") == IX:
            return True
    return False

def upgrade():
    conn = op.get_bind()
    if not _has_column(conn):
        op.add_column(TABLE, sa.Column(COL, sa.String(length=64), nullable=True))
    if not _has_index(conn):
        op.create_index(IX, TABLE, ["org_id", COL], unique=True)

def downgrade():
    conn = op.get_bind()
    if _has_index(conn):
        op.drop_index(IX, table_name=TABLE)
    # No drop column by default (safe downgrade); uncomment if you really want:
    # if _has_column(conn):
    #     op.drop_column(TABLE, COL)
