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

echo "==> Arrancar solo postgres primero"
docker compose up -d postgres
echo "   ... esperando a que Postgres esté healthy"
# espera simple basada en healthcheck del servicio
for i in {1..40}; do
  state="$(docker compose ps --format json | jq -r '.[] | select(.Service=="postgres") | .State')"
  if [ "$state" = "running" ]; then break; fi
  sleep 1
done

echo "==> Arrancar backend"
docker compose up -d --build backend

echo "==> Logs recientes de backend (si falla algo, lo veremos aquí)"
docker compose logs --tail=120 backend || true

echo "==> Verificación interna desde el contenedor backend"
# 1) Muestra DATABASE_URL, connect a DB, verifica search_path y uuid_generate_v4()
docker compose exec -T backend sh -lc 'python - <<PY
import os, sys
from sqlalchemy import create_engine, text
db = os.environ.get("DATABASE_URL")
print("DATABASE_URL=", db)
try:
    e = create_engine(db, future=True)
    with e.connect() as c:
        sp = c.execute(text("show search_path")).scalar_one()
        u  = c.execute(text("select uuid_generate_v4()")).scalar_one()
        print("search_path=", sp)
        print("uuid_generate_v4()=", u)
except Exception as ex:
    print("DB_CHECK_ERROR:", ex)
    sys.exit(1)
PY'

# 2) Espera activa a que el HTTP esté arriba en 127.0.0.1:8000
echo "==> Esperando HTTP interno en 127.0.0.1:8000 ..."
docker compose exec -T backend sh -lc 'python - <<PY
import socket, time, sys
addr=("127.0.0.1", 8000)
for i in range(60):
    try:
        s=socket.create_connection(addr, timeout=0.5)
        s.close()
        print("HTTP socket OK")
        sys.exit(0)
    except Exception:
        time.sleep(0.5)
print("HTTP socket NO OK")
sys.exit(1)
PY'

# 3) Probar /api/health y, si falla, /health; imprimir qué responde
echo "==> Probar /api/health y /health desde dentro del contenedor"
docker compose exec -T backend sh -lc 'python - <<PY
import urllib.request, json, sys
def try_get(path):
    url=f"http://127.0.0.1:8000{path}"
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            body=r.read().decode("utf-8", "ignore")
            print(f"{path} -> {r.status} {r.reason} | body: {body[:200]}")
            return True
    except Exception as e:
        print(f"{path} -> ERROR: {e}")
        return False

ok = try_get("/api/health")
if not ok:
    try_get("/health")
PY'

# 4) (Opcional) prueba desde el host si hay curl
if command -v curl >/dev/null 2>&1; then
  echo "==> Probar desde host: curl -sf http://localhost:8000/api/health"
  if curl -sf http://localhost:8000/api/health >/dev/null; then
    echo "Backend OK desde host (/api/health)"
  else
    echo "⚠️  /api/health no respondió desde host; probando /health"
    curl -sf http://localhost:8000/health >/dev/null && echo "Backend OK desde host (/health)" || echo "❌ Tampoco /health en host"
  fi
else
  echo "Host sin curl, omito prueba externa"
fi

echo "==> Hecho"
