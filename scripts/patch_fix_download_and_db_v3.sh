#!/usr/bin/env bash
set -euo pipefail

START_DIR="$(pwd)"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Localiza docker-compose.yml
CANDIDATES=(
  "$START_DIR/docker-compose.yml"
  "$ROOT/docker-compose.yml"
  "$ROOT/forge_saas/docker-compose.yml"
  "$START_DIR/forge_saas/docker-compose.yml"
)
COMPOSE_FILE=""
for f in "${CANDIDATES[@]}"; do
  [ -f "$f" ] && COMPOSE_FILE="$f" && break
done
[ -z "$COMPOSE_FILE" ] && { echo "❌ No encontré docker-compose.yml"; exit 1; }

COMPOSE_DIR="$(dirname "$COMPOSE_FILE")"
echo "✅ Usando compose en: $COMPOSE_FILE"
cd "$COMPOSE_DIR"

echo "==> Backups"
cp -n docker-compose.yml docker-compose.yml.bak 2>/dev/null || true

echo "==> Normalizar Postgres (usuario/clave/db = forge)"
sed -i -E 's/(POSTGRES_USER:).*/\1 forge/' docker-compose.yml || true
sed -i -E 's/(POSTGRES_PASSWORD:).*/\1 forge/' docker-compose.yml || true
sed -i -E 's/(POSTGRES_DB:).*/\1 forge/' docker-compose.yml || true

echo "==> Normalizar DATABASE_URL del backend"
if grep -qE 'DATABASE_URL:' docker-compose.yml; then
  sed -i -E 's#(DATABASE_URL:\s*).+#\1postgresql+psycopg2://forge:forge@postgres:5432/forge#' docker-compose.yml
fi
sed -i -E 's#postgresql\+psycopg2://postgres:postgres@postgres:5432/postgres#postgresql+psycopg2://forge:forge@postgres:5432/forge#g' docker-compose.yml || true

# ¿Existe UI?
NEED_UI=0
if [ -d ui ] && [ -f ui/Dockerfile ]; then
  NEED_UI=1
else
  echo "AVISO: no hay carpeta ui/ (o falta Dockerfile). Omito construir/arrancar 'ui'."
fi

echo "==> Reconstruir y arrancar servicios"
if [ "$NEED_UI" -eq 1 ]; then
  docker compose up -d --build backend ui
else
  docker compose up -d --build backend
fi

echo "==> Comprobación rápida de salud del backend"
sleep 1
if command -v curl >/dev/null 2>&1; then
  if curl -sf http://localhost:8000/api/health >/dev/null; then
    echo "Backend OK"
  else
    echo "⚠️  /api/health no responde en localhost:8000"
  fi
else
  echo "curl no está en el host, omito test HTTP"
fi

echo "Listo."
