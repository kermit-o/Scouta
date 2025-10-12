import re, sys, pathlib, json, subprocess, time

API = "http://localhost:8000"
path = pathlib.Path("backend/app/routers/projects.py")
bak = path.with_suffix(path.suffix + ".bak")

src = path.read_text(encoding="utf-8")

# 1) Normalizar prefix del router (por si alguien lo cambió)
src = re.sub(
    r'APIRouter\s*\(\s*prefix\s*=\s*["\']\/api\/projects["\'][^)]*\)',
    'APIRouter(prefix="/api/projects")',
    src,
)

# 2) Corregir decoradores con doble prefijo -> rutas relativas
patterns = [
    # variantes con /api/projects/{project_id}/run o duplicadas
    (r'@router\.post\(["\']/api/projects(?:/api/projects)?/\{project_id\}/run["\']\)', '@router.post("/{project_id}/run")'),
    (r'@router\.get\(["\']/api/projects(?:/api/projects)?/\{project_id\}/runs["\']\)', '@router.get("/{project_id}/runs")'),
]

changed = src
for pat, rep in patterns:
    changed = re.sub(pat, rep, changed)

if changed == src:
    print("Nada que cambiar (ya parece estar bien) o patrón no encontrado.")
else:
    # backup y escribir
    if not bak.exists():
        bak.write_text(src, encoding="utf-8")
    path.write_text(changed, encoding="utf-8")
    print(f"Parche aplicado en {path} (backup en {bak})")

# 3) Rebuild + restart backend
subprocess.run(["docker", "compose", "up", "-d", "--build", "backend"], check=True)
time.sleep(1.0)

# 4) Verificar OpenAPI
try:
    out = subprocess.check_output(["curl", "-sS", f"{API}/openapi.json"])
    paths = json.loads(out)["paths"].keys()
    runs = sorted([p for p in paths if re.match(r'^/api/projects/\{project_id\}/run(s)?$', p)])
    print("\nRutas detectadas:")
    for p in runs:
        print(p)
    if not runs:
        print("NO_RUN_ROUTES")
except Exception as e:
    print("No pude leer openapi.json:", e)
