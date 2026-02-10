#!/usr/bin/env bash
set -euo pipefail

ROOT="/workspaces/Scouta/backend_consolidate_20251015-1755/backend_reorganized"

TEMPLATE_APP_DIR="$ROOT/templates/forge_fastapi_pg_crud_v1/backend/app"
PROJECT_DIR="$ROOT/workdir/055a9ae0-b6c9-409d-af28-bdd5b3877f48"
PROJECT_APP_DIR="$PROJECT_DIR/backend/app"

echo "ROOT             => $ROOT"
echo "TEMPLATE_APP_DIR => $TEMPLATE_APP_DIR"
echo "PROJECT_DIR      => $PROJECT_DIR"
echo "PROJECT_APP_DIR  => $PROJECT_APP_DIR"
echo

if [ ! -d "$TEMPLATE_APP_DIR" ]; then
  echo "❌ No existe el template en: $TEMPLATE_APP_DIR"
  exit 1
fi

if [ ! -d "$PROJECT_APP_DIR" ]; then
  echo "❌ No existe backend/app en el proyecto generado: $PROJECT_APP_DIR"
  exit 1
fi

# 1) Backup de backend/app generado (por si acaso)
BACKUP_DIR="$PROJECT_DIR/backend/app_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Haciendo backup de backend/app en: $BACKUP_DIR"
cp -R "$PROJECT_APP_DIR" "$BACKUP_DIR"

# 2) Copiar estructura del template sobre el proyecto
#    Respetamos app.db del proyecto generado si existe.
echo "📥 Copiando template sobre backend/app (sin tocar app.db si existe)..."
rsync -av \
  --exclude 'app.db' \
  "$TEMPLATE_APP_DIR"/ \
  "$PROJECT_APP_DIR"/

echo
echo "Contenido final de backend/app:"
tree "$PROJECT_APP_DIR" || ls -R "$PROJECT_APP_DIR"

echo
echo "✅ Template inyectado en el proyecto generado."
echo "Ahora puedes levantar el backend e-commerce con Docker:"
echo
echo "  cd \"$PROJECT_DIR\""
echo "  docker rm -f ecommerce-app 2>/dev/null || true"
echo "  docker run --rm -d --name ecommerce-app \\"
echo "    -e DATABASE_URL='sqlite:////app/backend/app/app.db' \\"
echo "    -v \"\$PWD:/app\" -w /app \\"
echo "    -p 8082:8081 \\"
echo "    python:3.12 bash -lc \\"
echo "    \"pip install -r backend/app/requirements.txt && \\"
echo "     python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8081\""
echo
echo "Luego prueba:"
echo "  curl -s http://localhost:8082/api/health ; echo"
echo "  curl -s http://localhost:8082/openapi.json | jq '.paths | keys'"
