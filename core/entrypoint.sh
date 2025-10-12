#!/bin/sh
set -e

echo "[entrypoint] running migrations..."
alembic upgrade head || true

echo "[entrypoint] starting uvicorn..."
# Permite override vía env, por defecto usa app.main:app
UVICORN_APP="${UVICORN_APP:-app.main:app}"
PORT="${PORT:-8000}"
