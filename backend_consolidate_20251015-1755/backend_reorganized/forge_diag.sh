#!/usr/bin/env bash
set -euo pipefail

# ------------------ helpers ------------------
ts() { date +"%Y-%m-%d %H:%M:%S%z"; }
log() { printf "[%s] %s\n" "$(ts)" "$*" >&2; }
exists() { command -v "$1" >/dev/null 2>&1; }

mask_line() {
  # enmascara valores de .env con patrones sensibles
  local line="$1"
  if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
    printf "%s\n" "$line"
    return
  fi
  local key="${line%%=*}"
  local val="${line#*=}"
  if [[ "$key" =~ (SECRET|TOKEN|KEY|PASS|PWD|WEBHOOK|API|BEARER) ]]; then
    # deja últimos 4 caracteres visibles, resto ****
    local tail="${val: -4}"
    printf "%s=%s%s\n" "$key" "****" "$tail"
  else
    printf "%s\n" "$line"
  fi
}

port_of() {
  # docker compose port SERVICE PRIVATEPORT -> host:port
  $DC port "$1" "$2" 2>/dev/null | head -n1 | tr -d '[:space:]'
}

try_curl() {
  local url="$1"
  curl -fsSL --max-time 5 "$url" 2>/dev/null || true
}

try_head() {
  local url="$1"
  curl -fsI --max-time 5 "$url" 2>/dev/null || true
}

try_psql() {
  local cid="$1"
  local dbs=("forge" "postgres")
  local out=""
  for db in "${dbs[@]}"; do
    if out=$(docker exec -i "$cid" psql -U postgres -d "$db" -c "select current_database(), version();" 2>/dev/null); then
      echo "::connected:$db"
      echo "$out"
      docker exec -i "$cid" psql -U postgres -d "$db" -c "select extname from pg_extension order by 1;" 2>/dev/null || true
      return 0
    fi
  done
  echo "::could_not_connect"
  return 1
}

# ------------------ setup ------------------
ROOT="$(pwd)"
REPORT="forge_report_$(date +%Y%m%d_%H%M%S).md"

# detect docker compose v2/v1
if exists docker && docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif exists docker-compose; then
  DC="docker-compose"
else
  echo "Docker Compose no encontrado. Instálalo y vuelve a ejecutar." >&2
  exit 1
fi

# validar compose file
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
if [[ ! -f "$COMPOSE_FILE" ]]; then
  # intentar rutas comunes
  for f in docker-compose.yml compose.yml docker/compose.yml; do
    [[ -f "$f" ]] && COMPOSE_FILE="$f" && break
  done
fi
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "No encuentro docker-compose.yml en $(pwd). Ponme en la raíz del proyecto." >&2
  exit 1
fi

# ------------------ inicio de informe ------------------
{
echo "# Forge SaaS — Diagnóstico"
echo "- Fecha: $(ts)"
echo "- Raíz: \`$ROOT\`"
echo "- Compose: \`$DC\` | Archivo: \`$COMPOSE_FILE\`"
echo

echo "## Servicios en Compose"
$DC -f "$COMPOSE_FILE" config --services 2>/dev/null || echo "_No se pudo listar servicios_"
echo

echo "## Estado de contenedores"
$DC -f "$COMPOSE_FILE" ps
echo

echo "## Imágenes"
$DC -f "$COMPOSE_FILE" images || true
echo

echo "## .env (valores sensibles enmascarados)"
if [[ -f ".env" ]]; then
  while IFS= read -r line; do mask_line "$line"; done < .env
else
  echo "_No hay .env_"
fi
echo

# ------------------ puertos & health ------------------
echo "## Puertos resueltos"
BE_MAP="$(port_of backend 8000 || true)"
UI_MAP="$(port_of ui 8501 || true)"
DB_MAP="$(port_of db 5432 || true)"
echo "- backend 8000 -> ${BE_MAP:-no-expuesto}"
echo "- ui 8501      -> ${UI_MAP:-no-expuesto}"
echo "- db 5432      -> ${DB_MAP:-no-expuesto}"
echo

echo "## Healthcheck backend"
if [[ -n "${BE_MAP:-}" ]]; then
  echo "### GET /api/health"
  try_curl "http://${BE_MAP}/api/health" | sed 's/^/    /'
  echo
  echo "### HEAD /artifact (si existe)"
  try_head "http://${BE_MAP}/artifact" | sed 's/^/    /'
else
  echo "_Backend no expuesto, no puedo consultar._"
fi
echo

echo "## UI (Streamlit) — ping raíz"
if [[ -n "${UI_MAP:-}" ]]; then
  try_head "http://${UI_MAP}/" | sed 's/^/    /'
else
  echo "_UI no expuesta._"
fi
echo

# ------------------ backend introspección ------------------
echo "## Backend — versión Python y paquetes clave"
BE_CID="$($DC -f "$COMPOSE_FILE" ps -q backend || true)"
if [[ -n "$BE_CID" ]]; then
  docker exec "$BE_CID" python -V 2>&1 | sed 's/^/    /' || true
  echo
  docker exec "$BE_CID" python -c "import sys; print(sys.executable)" 2>/dev/null | sed 's/^/    /' || true
  echo
  docker exec "$BE_CID" python -c "import pkgutil; print(sorted([m.name for m in pkgutil.iter_modules() if m.name in ('fastapi','alembic','sqlalchemy','psycopg2','psycopg')))" 2>/dev/null | sed 's/^/    /' || true
  echo

  echo "### Alembic — estado actual (si disponible)"
  docker exec "$BE_CID" bash -lc 'command -v alembic >/dev/null && alembic current || echo "alembic no instalado"' | sed 's/^/    /'
else
  echo "_No encuentro contenedor backend._"
fi
echo

# ------------------ base de datos ------------------
echo "## Base de Datos (Postgres)"
DB_CID="$($DC -f "$COMPOSE_FILE" ps -q db || true)"
if [[ -n "$DB_CID" ]]; then
  try_psql "$DB_CID" | sed 's/^/    /'
else
  echo "_No encuentro contenedor db._"
fi
echo

# ------------------ árbol y migraciones ------------------
echo "## Estructura relevante"
TREE_CMD="find . -maxdepth 3 -type d \( -name '.git' -o -name '__pycache__' -o -name '.venv' -o -name 'node_modules' \) -prune -o -print"
eval "$TREE_CMD" | sed 's/^/    /'
echo

echo "## Migrations (si existen)"
if [[ -d "backend/app/migrations" ]]; then
  find backend/app/migrations -maxdepth 2 -type f | sort | sed 's/^/    /'
elif [[ -d "app/migrations" ]]; then
  find app/migrations -maxdepth 2 -type f | sort | sed 's/^/    /'
else
  echo "    _No se encontró carpeta de migraciones estándar._"
fi
echo

# ------------------ logs ------------------
echo "## Logs recientes"
echo "### backend (últimas 200 líneas)"
$DC -f "$COMPOSE_FILE" logs --no-color --tail=200 backend 2>/dev/null | sed 's/^/    /' || echo "    _Sin logs_"
echo
echo "### db (últimas 100 líneas)"
$DC -f "$COMPOSE_FILE" logs --no-color --tail=100 db 2>/dev/null | sed 's/^/    /' || echo "    _Sin logs_"
echo
echo "### ui (últimas 100 líneas)"
$DC -f "$COMPOSE_FILE" logs --no-color --tail=100 ui 2>/dev/null | sed 's/^/    /' || echo "    _Sin logs_"
echo

# ------------------ networking ------------------
echo "## Redes Docker (compose)"
$DC -f "$COMPOSE_FILE" ps --format json 2>/dev/null || true
echo

} | tee "$REPORT" >/dev/null

log "Informe listo: $REPORT"
echo
echo "👉 Revisa el informe: $REPORT"
