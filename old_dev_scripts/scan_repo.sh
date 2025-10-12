#!/usr/bin/env bash
# dev/scan_repo.sh — Fotografía del proyecto (Forge SaaS)
set -Eeuo pipefail
shopt -s nullglob

ROOT="${1:-$(pwd)}"
DC="${DC:-docker compose}"

bar(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

bar "Ruta base"
echo "$ROOT"

bar "Árbol (filtrado)"
# Requiere 'tree'; si no, fallback con find
if command -v tree >/dev/null 2>&1; then
  tree -a -I '.git|.venv|__pycache__|*.pyc|node_modules|.pytest_cache|.mypy_cache|*.zip|*.log|.DS_Store' -L 4 "$ROOT"
else
  find "$ROOT" -maxdepth 4 \
    -not -path '*/.git/*' -not -path '*/.venv/*' -not -path '*/__pycache__/*' \
    -not -path '*/node_modules/*' -not -name '*.pyc' -not -name '*.zip' -not -name '*.log' \
    -printf '%y %p\n' | sed 's/^/  /'
fi

bar "docker compose services"
$DC ps || true

bar "docker compose env (ui/backend si existen)"
$DC config 2>/dev/null | awk '/services:/{p=1}p' | sed -n '1,200p' | sed -n '/ui:/,/^[^ ]/p;/backend:/,/^[^ ]/p' || true

bar "Backend: archivos clave"
ls -l backend/ 2>/dev/null || true
ls -l backend/app 2>/dev/null || true
printf "\nFastAPI app/main:\n"; grep -RIn 'FastAPI\(|APIRouter\(|@app\.' backend/app 2>/dev/null || true
printf "\nRouters:\n"; grep -RIn '@(get|post|put|patch|delete)\(' backend/app 2>/dev/null || true
printf "\nModelos SQLAlchemy:\n"; grep -RIn 'class .*Base|Column\(' backend/app 2>/dev/null || true
printf "\nAlembic (migrations):\n"; ls -l backend/migrations 2>/dev/null || true

bar "UI: archivos clave"
ls -l ui/ 2>/dev/null || true
printf "\nStreamlit pages:\n"; ls -1 ui/*.py ui/pages/*.py 2>/dev/null || true
printf "\nReferencias API (UI):\n"
grep -RIn --line-number --exclude-dir='.venv' --exclude-dir='.git' \
  -e 'PUBLIC_API_BASE' -e '\<api_base\>' -e 'http://localhost:8000' -e 'http://127\.0\.0\.1:8000' \
  -e 'requests\.(get|post)\(' -e 'urlopen\(' ui/ 2>/dev/null || true

bar ".env y settings (no imprime secretos, solo claves)"
for f in .env .env.example backend/.env ui/.env; do
  [ -f "$f" ] && echo "-- $f" && sed -E 's@(=).*@\1***@' "$f" | sed 's/^/  /'
done
[ -f config/settings.py ] && echo "-- config/settings.py" && sed -n '1,200p' config/settings.py | sed 's/^/  /' || true

bar "Líneas de código (LOC)"
if command -v cloc >/dev/null 2>&1; then
  cloc backend ui app 2>/dev/null || cloc .
else
  echo "Instala cloc para mejor reporte: sudo apt-get update && sudo apt-get install -y cloc"
  wc -l $(git ls-files '*.py' 2>/dev/null) 2>/dev/null | tail -n 1 || true
fi

bar "Salud (si containers arriba)"
if $DC ps >/dev/null 2>&1; then
  echo "- Backend:"; curl -fsS http://localhost:8000/api/health 2>/dev/null || echo "  no responde"
  echo "- UI:     "; curl -fsS http://localhost:8501 2>/dev/null | head -n 3 || echo "  no responde"
fi

bar "Sugerencia siguiente"
cat <<'EOF'
- Si todo ok: seguimos con el plan de multi-agente (jobs/agent_runs/artifacts + scheduler + /run).
- Si hay endpoints/routers faltantes, aquí arriba verás los huecos.
- Pega aquí la salida relevante y continuo con diffs mínimos listos.
EOF
