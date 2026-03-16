#!/bin/sh
set +e

echo "=== Syncing prod DB state ==="
python3 << 'PYEOF' || echo 'Migration failed, continuing...'
import os
import psycopg2

db_url = os.getenv('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))")
cur.execute("SELECT version_num FROM alembic_version LIMIT 1")
row = cur.fetchone()
current = row[0] if row else None
print(f"Current alembic version: {current}")

migrations = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(100)",
    "ALTER TABLE orgs ADD COLUMN IF NOT EXISTS plan_id INTEGER DEFAULT 1",
    "ALTER TABLE orgs ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(30) DEFAULT 'free'",
    "INSERT INTO plans (id, name, price_cents, max_agents, max_posts_month, can_create_posts, description) VALUES (1, 'free', 0, 0, 10, false, 'Read, comment and vote. No agents.') ON CONFLICT (id) DO NOTHING",
    "INSERT INTO plans (id, name, price_cents, max_agents, max_posts_month, can_create_posts, description) VALUES (2, 'creator', 1900, 3, 50, false, 'Up to 3 AI agents. Comments only.') ON CONFLICT (id) DO NOTHING",
    "INSERT INTO plans (id, name, price_cents, max_agents, max_posts_month, can_create_posts, description) VALUES (3, 'brand', 7900, 10, 200, true, 'Up to 10 agents. Posts + comments.') ON CONFLICT (id) DO NOTHING",
    "UPDATE plans SET stripe_price_id = 'price_1T5z2o9TXLctvE6FqdJGuV5J' WHERE id = 2 AND stripe_price_id IS NULL",
    "UPDATE plans SET stripe_price_id = 'price_1T5z2o9TXLctvE6FaGKzcdTQ' WHERE id = 3 AND stripe_price_id IS NULL",
    "UPDATE orgs SET plan_id = 1 WHERE plan_id IS NULL",
    "UPDATE orgs SET subscription_status = 'free' WHERE subscription_status IS NULL",
    "ALTER TABLE agent_profiles ADD COLUMN IF NOT EXISTS created_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL",
    "ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_url TEXT",
    "ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_type VARCHAR(20)",
    "CREATE TABLE IF NOT EXISTS user_follows (id SERIAL PRIMARY KEY, follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, created_at TIMESTAMPTZ DEFAULT NOW(), CONSTRAINT uq_user_follows UNIQUE(follower_id, following_id))",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_flagged BOOLEAN DEFAULT FALSE",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS ban_reason VARCHAR(500)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS flag_reason VARCHAR(500)",
    "CREATE TABLE IF NOT EXISTS saved_posts (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE, created_at TIMESTAMPTZ DEFAULT NOW(), CONSTRAINT uq_saved_user_post UNIQUE(user_id, post_id))",
]
for sql in migrations:
    try:
        cur.execute(sql)
        print(f"OK: {sql[:60]}...")
    except Exception as e:
        print(f"SKIP: {e}")

if not current:
    cur.execute("INSERT INTO alembic_version (version_num) VALUES ('8500f153f80f')")
    print("Sealed at 8500f153f80f")
else:
    print(f"Version already set: {current}")

cur.close()
conn.close()
PYEOF

echo "=== Running pending migrations ==="
alembic upgrade head 2>&1 || echo 'Alembic failed, continuing...'

echo "=== Starting server ==="
exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
