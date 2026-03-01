#!/bin/sh
set -e

echo "=== Stamping prod DB if needed ==="
python3 << 'PYEOF'
import os
import psycopg2

db_url = os.getenv('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

# Conexión directa con psycopg2 para control total de transacciones
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

# Verificar si existe alembic_version
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'alembic_version'
    )
""")
exists = cur.fetchone()[0]

if not exists:
    print("No alembic_version table found. Creating and stamping eab4a0091729...")
    cur.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))")
    cur.execute("INSERT INTO alembic_version (version_num) VALUES ('eab4a0091729')")
    print("Stamped OK.")
else:
    cur.execute("SELECT version_num FROM alembic_version LIMIT 1")
    row = cur.fetchone()
    if row:
        print(f"alembic_version exists: {row[0]}")
    else:
        print("Table exists but empty. Inserting eab4a0091729...")
        cur.execute("INSERT INTO alembic_version (version_num) VALUES ('eab4a0091729')")
        print("Stamped OK.")

cur.close()
conn.close()
PYEOF

echo "=== Running Alembic migrations ==="
alembic upgrade head

echo "=== Starting server ==="
exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
