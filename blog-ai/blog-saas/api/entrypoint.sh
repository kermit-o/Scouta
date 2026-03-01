#!/bin/sh
set -e

echo "=== Stamping prod DB if needed ==="
# Si no hay alembic_version, sellar en eab4a0091729 (estado actual de prod)
python3 -c "
import os
from sqlalchemy import create_engine, text

db_url = os.getenv('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(db_url)
with engine.connect() as conn:
    try:
        result = conn.execute(text('SELECT version_num FROM alembic_version LIMIT 1'))
        row = result.fetchone()
        if row:
            print(f'alembic_version exists: {row[0]}')
        else:
            print('No version found, stamping eab4a0091729...')
            conn.execute(text(\"INSERT INTO alembic_version (version_num) VALUES ('eab4a0091729')\"))
            conn.commit()
            print('Stamped.')
    except Exception as e:
        print(f'No alembic_version table, creating and stamping: {e}')
        conn.execute(text('CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))'))
        conn.execute(text(\"INSERT INTO alembic_version (version_num) VALUES ('eab4a0091729') ON CONFLICT DO NOTHING\"))
        conn.commit()
        print('Stamped.')
"

echo "=== Running Alembic migrations ==="
alembic upgrade head

echo "=== Starting server ==="
exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
