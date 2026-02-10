#!/usr/bin/env bash
set -euo pipefail
ROOT="backend_consolidate_20251015-1755/backend"
COMPOSE="backend_consolidate_20251015-1755/docker/compose.yml"

echo "=== 1) Archivos ai_analysis.py en el host ==="
find "$ROOT" -type f -name "ai_analysis.py" -print

echo
echo "=== 2) Grep en host: referencias a ProjectSupervisor / SupervisorSimple ==="
grep -RIn --color=always -E 'from .*ProjectSupervisor|ProjectSupervisor\(|from .*SupervisorSimple|SupervisorSimple\(' "$ROOT" || true

echo
echo "=== 3) ¿Qué copia Docker al contenedor? (Dockerfile y compose) ==="
echo "--- Dockerfile.backend (si existe) ---"
sed -n '1,120p' backend_consolidate_20251015-1755/docker/Dockerfile.backend 2>/dev/null || echo "No Dockerfile.backend"
echo "--- compose.yml (servicio backend) ---"
awk '/services:/,/^[^ ]/{print} /backend:/{flag=1} flag{print} /^  [a-zA-Z0-9_-]+:/{if($1!="  backend:") exit}' "$COMPOSE" || true

echo
echo "=== 4) Dentro del contenedor: módulo realmente cargado ==="
# Levanta el backend si no está
docker compose -f "$COMPOSE" up -d backend >/dev/null
# Ejecuta un Python dentro del contenedor para inspeccionar el módulo
docker compose -f "$COMPOSE" exec -T backend python - <<'PY' || echo "__PY_ERROR__"
import importlib, inspect, sys
print("Python:", sys.version)
try:
    m = importlib.import_module("backend.app.api.ai_analysis")
    print("ai_analysis.__file__ =", m.__file__)
    src = open(m.__file__, "r", encoding="utf-8").read()
    print("\n--- primeras 80 líneas de ai_analysis.py (contenedor) ---")
    print("\n".join(src.splitlines()[:80]))
    print("\n--- huella ---")
    print("Tiene 'ProjectSupervisor(' ?", "ProjectSupervisor(" in src)
    print("Tiene 'SupervisorSimple('  ?", "SupervisorSimple(" in src)
    print("Línea import DeepSeekClient:", [ln for ln in src.splitlines() if "DeepSeekClient" in ln][:3])
except Exception as e:
    print("ERROR importando backend.app.api.ai_analysis:", e)
PY

echo
echo "=== 5) ¿Qué supervisor existe en core? (contenedor) ==="
docker compose -f "$COMPOSE" exec -T backend python - <<'PY' || true
import pkgutil
import backend.core.agents as agents
mods = [m.name for m in pkgutil.iter_modules(agents.__path__)]
print("core.agents modules:", sorted(mods)[:30], " ...")
PY

echo
echo "=== 6) Últimos logs del backend ==="
docker compose -f "$COMPOSE" logs backend --tail=200 || true
