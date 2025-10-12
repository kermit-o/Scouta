#!/usr/bin/env bash
set -Eeuo pipefail
DC="${DC:-docker compose}"

echo "== Alembic current/heads =="
$DC run --rm -T backend alembic current
$DC run --rm -T backend alembic heads

echo "== psql: tablas en public =="
$DC exec -T postgres psql -U forge -d forge -c "\dt+"

echo "== columnas clave =="
$DC exec -T postgres psql -U forge -d forge -c "\d+ projects"
$DC exec -T postgres psql -U forge -d forge -c "\d+ jobs"
$DC exec -T postgres psql -U forge -d forge -c "\d+ agent_runs"
$DC exec -T postgres psql -U forge -d forge -c "\d+ artifacts"
