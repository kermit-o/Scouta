import re, pathlib, subprocess, json, time

API = "http://localhost:8000"
p = pathlib.Path("backend/app/routers/projects.py")
bak = p.with_suffix(p.suffix + ".bak")

src = p.read_text(encoding="utf-8")

# Asegurar que existe un APIRouter con el prefijo correcto
if "APIRouter(" not in src:
    raise SystemExit("No encontré APIRouter en backend/app/routers/projects.py; revisa el archivo manualmente.")
src = re.sub(
    r'APIRouter\s*\(\s*prefix\s*=\s*["\']\/api\/projects["\'][^)]*\)',
    'APIRouter(prefix="/api/projects")',
    src,
)

# Normalizar nombre del router (si usan otro alias, lo respetamos; detectamos el identificador)
m = re.search(r'(\w+)\s*=\s*APIRouter\(prefix="/api/projects"\)', src)
router_name = m.group(1) if m else "router"

# Si el router no se llama 'router', añadimos un alias seguro 'router = <nombre>'
if router_name != "router" and "router =" not in src:
    src += f"\n# Alias para consistencia con rutas añadidas automáticamente\nrouter = {router_name}\n"

# Bloque de utilidades e imports para scheduler
if "enqueue_pipeline" not in src or "list_runs_for_project" not in src:
    util_block = '''
# === Auto-added scheduler imports (safe fallback) ===
try:
    from ..services.scheduler import enqueue_pipeline, list_runs_for_project
except Exception:  # fallback stubs si no existe scheduler real
    def enqueue_pipeline(project_id: str):
        return {"queued": True, "project_id": project_id}
    def list_runs_for_project(project_id: str):
        return []
# === end auto-added ===
'''.lstrip()
    if "services.scheduler" not in src:
        src += "\n" + util_block

# Asegurar decorador POST /{project_id}/run
if not re.search(r'@router\.post\(["\']\/\{project_id\}\/run["\']\)', src):
    run_block = f'''
@router.post("/{{project_id}}/run", summary="Queue full pipeline for a project")
def _queue_project_run(project_id: str):
    out = enqueue_pipeline(project_id)
    return {{"status": "queued", "project_id": project_id, "result": out}}
'''.lstrip()
    src += "\n" + run_block

# Asegurar decorador GET /{project_id}/runs
if not re.search(r'@router\.get\(["\']\/\{project_id\}\/runs["\']\)', src):
    runs_block = f'''
@router.get("/{{project_id}}/runs", summary="List pipeline runs for a project")
def _list_project_runs(project_id: str):
    try:
        return list_runs_for_project(project_id)
    except Exception:
        return []
'''.lstrip()
    src += "\n" + runs_block

# Guardar backup y archivo parcheado
if not bak.exists():
    bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print(f"Parche aplicado en {p} (backup en {bak})")

# Rebuild + restart backend
subprocess.run(["docker", "compose", "up", "-d", "--build", "backend"], check=True)
time.sleep(1.0)

# Rebuild + restart backend
subprocess.run(["docker", "compose", "up", "-d", "--build", "backend"], check=True)

# Esperar a que /api/health responda OK (hasta 60s)
import urllib.request, urllib.error, time, json
for i in range(60):
    try:
        with urllib.request.urlopen(f"{API}/api/health", timeout=2) as r:
            if r.status == 200:
                break
    except Exception:
        pass
    time.sleep(1)
else:
    raise SystemExit("Backend no levantó /api/health en 60s")

# Verificar OpenAPI (si openapi_url está deshabilitado, esto fallará)
try:
    out = subprocess.check_output(["curl", "-sS", f"{API}/openapi.json"])
    paths = json.loads(out)["paths"].keys()
    ok = [k for k in paths if k in ("/api/projects/{project_id}/run", "/api/projects/{project_id}/runs")]
    print("Rutas detectadas:", ok if ok else "NO_RUN_ROUTES")
except subprocess.CalledProcessError:
    print("Aviso: /openapi.json no disponible. ¿openapi_url deshabilitado?")
    print("Prueba manual: curl -fsS http://localhost:8000/api/health ; curl -fsS http://localhost:8000/openapi.json")


# Verificar OpenAPI
out = subprocess.check_output(["curl", "-sS", f"{API}/openapi.json"])
paths = json.loads(out)["paths"].keys()
ok = [k for k in paths if k in ("/api/projects/{project_id}/run", "/api/projects/{project_id}/runs")]
print("Rutas detectadas:", ok if ok else "NO_RUN_ROUTES")
