#!/bin/sh
set -e

echo "=== Stamping prod DB if needed ==="
python3 << 'PYEOF'
import os
import psycopg2

db_url = os.getenv('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

# Ver si alembic_version existe y qué tiene
cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
exists = cur.fetchone()[0]

if not exists:
    cur.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))")
    print("Created alembic_version table")

cur.execute("SELECT version_num FROM alembic_version LIMIT 1")
row = cur.fetchone()
current = row[0] if row else None
print(f"Current version: {current}")

# Ver qué tablas existen para determinar el estado real
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables in prod: {tables}")

has_plans = 'plans' in tables
has_subscriptions = 'subscriptions' in tables
has_stripe_col = False

if 'users' in tables:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='stripe_customer_id'")
    has_stripe_col = cur.fetchone() is not None

print(f"plans={has_plans}, subscriptions={has_subscriptions}, stripe_col={has_stripe_col}")

# Si todo ya existe, sellar en 8500f153f80f
if has_plans and has_subscriptions and has_stripe_col:
    if not current:
        cur.execute("INSERT INTO alembic_version (version_num) VALUES ('8500f153f80f')")
    else:
        cur.execute("UPDATE alembic_version SET version_num = '8500f153f80f'")
    print("Sealed at 8500f153f80f (everything already exists)")
elif not current:
    cur.execute("INSERT INTO alembic_version (version_num) VALUES ('eab4a0091729')")
    print("Sealed at eab4a0091729")

cur.close()
conn.close()
PYEOF

echo "=== Running Alembic migrations ==="
alembic upgrade head

echo "=== Starting server ==="
exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
