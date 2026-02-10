#!/usr/bin/env bash
# Levanta el ÚLTIMO backend generado usando SQLite local.
# Requisitos:
#  - Estar dentro del venv de Scouta (source .venv/bin/activate)
#  - Tener alembic instalado en el venv (una vez: pip install alembic)

set -e  # no usamos -u por el lío con RVM

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Forge :: run_latest_generated_backend_sqlite =="

# 1) Detectar el último workdir generado
LATEST_WORKDIR="$(ls -dt workdir/*/ 2>/dev/null | head -n1 || true)"

if [ -z "$LATEST_WORKDIR" ]; then
  echo "❌ No se encontró ningún workdir en $ROOT_DIR/workdir"
  exit 1
fi

LATEST_WORKDIR="${LATEST_WORKDIR%/}"
echo "Usando workdir: $LATEST_WORKDIR"

cd "$LATEST_WORKDIR"

# 2) Comprobar que existen archivos clave
if [ ! -f "backend/app/main.py" ] || [ ! -f "alembic.ini" ]; then
  echo "❌ Este workdir no tiene backend/app/main.py o alembic.ini. Abortando."
  exit 1
fi

# 3) Preparar entorno Python
# Asumimos que ya estás en el venv correcto (.venv de Scouta)
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

# DB SQLite dentro de backend/app
export DATABASE_URL="${DATABASE_URL:-sqlite:////$(pwd)/backend/app/app.db}"
echo "DATABASE_URL => $DATABASE_URL"

# 4) Asegurar que alembic está instalado en este entorno
if ! command -v alembic >/dev/null 2>&1; then
  echo "ℹ️ alembic no encontrado en PATH, instalando en el venv actual..."
  python -m pip install -q alembic
fi

echo "== Ejecutando migraciones Alembic (sqlite) =="
alembic -c alembic.ini upgrade head

echo "== Lanzando uvicorn backend.app.main:app en 0.0.0.0:8081 =="
echo "   (CTRL+C para parar)"

uvicorn backend.app.main:app --host 0.0.0.0 --port 8081
