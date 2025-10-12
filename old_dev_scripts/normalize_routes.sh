#!/usr/bin/env bash
set -euo pipefail

ROUTER="backend/app/routers/projects.py"
MAIN="backend/app/main.py"

cp -n "$ROUTER" "$ROUTER.bak" || true
cp -n "$MAIN" "$MAIN.bak" || true

# En el router, forzamos decoradores relativos (nada que empiece por /api/)
# @router.get("/api/projects/...") -> @router.get("/...")
sed -i 's#@router\.\(get\|post\|put\|delete\)(\s*"/api/projects/#@router.\1("/#g' "$ROUTER"

# Asegura que el include_router tenga prefix="/api/projects"
# y no esté repetido más de una vez.
if ! grep -q 'include_router(projects_router, prefix="/api/projects"' "$MAIN"; then
  # Inserta (si no existe) una sola vez
  python - "$MAIN" <<'PY'
import sys, re, io
p = sys.argv[1]
s = open(p, 'r', encoding='utf-8').read()
if 'from .routers import projects as projects_router' not in s:
    s = s.replace('from fastapi import FastAPI',
                  'from fastapi import FastAPI\nfrom .routers import projects as projects_router')
if 'include_router(projects_router' not in s:
    s = s.replace('app = FastAPI(', 
                  'app = FastAPI(')  # keep position
    s = s.replace('app = FastAPI(', 'app = FastAPI(')  # noop but ensures only one hit
    # añade el include después de crear app
    s = re.sub(r'(app = FastAPI\([^\)]*\)\n)', r'\1\napp.include_router(projects_router, prefix="/api/projects")\n', s, count=1, flags=re.M)
open(p, 'w', encoding='utf-8').write(s)
print("MAIN normalized")
PY
fi

echo "Router & main normalizados."
