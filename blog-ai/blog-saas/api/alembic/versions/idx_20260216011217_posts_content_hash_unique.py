from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "idx_20260216011217_posts_content_hash_unique"
down_revision = "fix_20260215005716_posts_pk_autoinc"
branch_labels = None
depends_on = None

TABLE = "posts"
COL = "content_hash"
UX = "uq_posts_org_content_hash"

def _has_column(conn, table: str, col: str) -> bool:
    insp = inspect(conn)
    return any(c["name"] == col for c in insp.get_columns(table))

def _has_index(conn, index_name: str) -> bool:
    insp = inspect(conn)
    for ix in insp.get_indexes(TABLE):
        if ix.get("name") == index_name:
            return True
    return False

def upgrade():
    conn = op.get_bind()

    if not _has_column(conn, TABLE, COL):
        op.add_column(TABLE, sa.Column(COL, sa.String(64), nullable=True))

    # unique (org_id, content_hash) — allow multiple NULLs (SQLite ok)
    if not _has_index(conn, UX):
        op.create_index(UX, TABLE, ["org_id", COL], unique=True)

def downgrade():
    conn = op.get_bind()
    if _has_index(conn, UX):
        op.drop_index(UX, table_name=TABLE)
    if _has_column(conn, TABLE, COL):
        op.drop_column(TABLE, COL)
