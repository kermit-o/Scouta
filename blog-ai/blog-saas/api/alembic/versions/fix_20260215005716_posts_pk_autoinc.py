from alembic import op

# revision identifiers, used by Alembic.
revision = "fix_20260215005716_posts_pk_autoinc"
down_revision = "idx_20260212234344_unique_agent_actions_idempotency_key"
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    if conn.dialect.name != "sqlite":
        return

    # 1) new table with proper PK + needed columns
    op.execute("""
    CREATE TABLE posts__new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER NOT NULL,
        author_user_id INTEGER,
        author_agent_id INTEGER,
        author_type TEXT NOT NULL DEFAULT 'user',
        title TEXT NOT NULL,
        slug TEXT NOT NULL,
        body_md TEXT NOT NULL DEFAULT '',
        excerpt TEXT,
        post_metadata TEXT,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at NUM,
        published_at NUM
    );
    """)

    # 2) copy data (best-effort)
    # If old 'id' has duplicates or nulls, SQLite will fail here.
    op.execute("""
    INSERT INTO posts__new (
        id, org_id, author_user_id, title, slug, body_md, status,
        created_at, published_at, author_type, author_agent_id, excerpt, post_metadata
    )
    SELECT
        id, org_id, author_user_id, title, slug, body_md, status,
        created_at, published_at, author_type, author_agent_id, excerpt, post_metadata
    FROM posts;
    """)

    # 3) swap tables
    op.execute("DROP TABLE posts;")
    op.execute("ALTER TABLE posts__new RENAME TO posts;")

    # 4) indexes (match what app expects)
    op.execute("CREATE INDEX IF NOT EXISTS ix_posts_org_id ON posts(org_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_posts_slug ON posts(slug);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_posts_org_status_created ON posts(org_id, status, created_at);")

def downgrade():
    conn = op.get_bind()
    if conn.dialect.name != "sqlite":
        return
    # no-op (downgrade would be destructive)
    return
