#!/usr/bin/env bash
set -euo pipefail

FILE="${1:-}"

if [[ -z "${FILE}" ]]; then
  # Autodetectar archivo que contenga FastAPI(
  mapfile -t candidates < <(grep -RIl --include='*.py' 'FastAPI(' . || true)
  if ((${#candidates[@]}==0)); then
    echo "❌ No encontré ningún archivo con 'FastAPI(' en el repo."
    echo "   Ejemplo manual: ./scripts/patch_20250920_backend_progress_guard.sh backend/app/main.py"
    exit 1
  fi
  if ((${#candidates[@]}>1)); then
    echo "⚠️ Encontré varios candidatos, elige uno y vuelve a ejecutar con la ruta:"
    printf '   • %s\n' "${candidates[@]}"
    exit 1
  fi
  FILE="${candidates[0]}"
fi

if [[ ! -f "$FILE" ]]; then
  echo "❌ No existe $FILE. Pasa una ruta válida."
  exit 1
fi

echo "🔧 Objetivo: $FILE"

python3 - "$FILE" <<'PY'
import io, os, re, sys
p = sys.argv[1]
with open(p, "r", encoding="utf-8") as f:
    s = f.read()

# 1) Añadir imports si faltan
added = False
if "from fastapi.responses import JSONResponse" not in s:
    s = s.replace("\n", "\nfrom fastapi.responses import JSONResponse\n", 1) if "\n" in s else s + "\nfrom fastapi.responses import JSONResponse\n"
    added = True
if "from starlette.requests import Request" not in s:
    s = s.replace("\n", "\nfrom starlette.requests import Request\n", 1) if "\n" in s else s + "\nfrom starlette.requests import Request\n"
    added = True

# 2) Asegurar redirect_slashes=False en la PRIMERA app = FastAPI(...)
def add_kw(arglist: str) -> str:
    if re.search(r'\bredirect_slashes\s*=', arglist):
        return arglist
    arglist = arglist.strip()
    return ("redirect_slashes=False" if not arglist else "redirect_slashes=False, " + arglist)

s, n = re.subn(
    r'(app\s*=\s*FastAPI\()\s*([^)]*)\)',
    lambda m: m.group(1) + add_kw(m.group(2)) + ")",
    s,
    count=1,
)

# 3) Inyectar middleware si no existe
if "PATCH 2025-09-20: progress guard" not in s:
    guard = '''
# PATCH 2025-09-20: progress guard
@app.middleware("http")
async def _progress_guard(request: Request, call_next):
    p = request.url.path
    # /api/progress o /api/progress/
    if p.rstrip("/") == "/api/progress":
        return JSONResponse(status_code=400, content={"detail": "Missing job_id"})
    # /api/progress/<id> con valores nulos/comunes
    if p.startswith("/api/progress/"):
        last = p.split("/")[-1].lower()
        if last in {"null", "none", "undefined", ""}:
            return JSONResponse(status_code=400, content={"detail": "Invalid job_id"})
    return await call_next(request)
'''
    # Lo colocamos después de la primera línea que define app = FastAPI(...)
    m = re.search(r'app\s*=\s*FastAPI\([^)]*\)\s*', s)
    if m:
        s = s[:m.end()] + "\n" + guard + s[m.end():]
    else:
        s += "\n" + guard

with open(p, "w", encoding="utf-8") as f:
    f.write(s)
print(f"✅ Parche aplicado a {p}")
PY

echo "✅ Listo."
