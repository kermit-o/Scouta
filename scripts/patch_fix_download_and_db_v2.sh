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
  if [ -f "$f" ]; then COMPOSE_FILE="$f"; break; fi
done
if [ -z "$COMPOSE_FILE" ]; then
  echo "❌ No encontré docker-compose.yml (probé: ${CANDIDATES[*]})"
  exit 1
fi
COMPOSE_DIR="$(dirname "$COMPOSE_FILE")"
echo "✅ Usando compose en: $COMPOSE_FILE"
cd "$COMPOSE_DIR"

echo "==> Backups"
cp -n docker-compose.yml docker-compose.yml.bak 2>/dev/null || true
[ -f ui/app.py ] && cp -n ui/app.py ui/app.py.bak 2>/dev/null || true

echo "==> Normalizar Postgres (usuario/clave/db = forge)"
sed -i -E 's/(POSTGRES_USER:).*/\1 forge/' docker-compose.yml || true
sed -i -E 's/(POSTGRES_PASSWORD:).*/\1 forge/' docker-compose.yml || true
sed -i -E 's/(POSTGRES_DB:).*/\1 forge/' docker-compose.yml || true

echo "==> Normalizar DATABASE_URL del backend"
if grep -qE 'DATABASE_URL:' docker-compose.yml; then
  sed -i -E 's#(DATABASE_URL:\s*).+#\1postgresql+psycopg2://forge:forge@postgres:5432/forge#' docker-compose.yml
fi
sed -i -E 's#postgresql\+psycopg2://postgres:postgres@postgres:5432/postgres#postgresql+psycopg2://forge:forge@postgres:5432/forge#g' docker-compose.yml || true

echo "==> Parchear UI para descarga correcta del ZIP"
if [ -f ui/app.py ]; then
  cat > ui/app.py <<'PY'
import os
from urllib.parse import urljoin
import streamlit as st
from utils import api

PUBLIC_API_BASE = os.getenv("PUBLIC_API_BASE", "http://localhost:8000").rstrip("/")

def to_public_url(path_or_url: str) -> str:
    if not path_or_url:
        return ""
    if path_or_url.startswith("/"):
        return urljoin(PUBLIC_API_BASE + "/", path_or_url.lstrip("/"))
    return (path_or_url
            .replace("http://backend:8000", PUBLIC_API_BASE)
            .replace("http://backend", PUBLIC_API_BASE))

st.set_page_config(page_title="Forge – Project Builder", layout="centered")
st.title("Forge – Project Builder")

with st.sidebar:
    st.caption(f"API_BASE: `{api.API_BASE}`")
    try:
        st.success("Backend healthy")
        st.json(api.health(), expanded=False)
    except Exception as e:
        st.error(f"Backend no responde: {e}")

st.subheader("Create project")
with st.form("create_project"):
    user_id = st.text_input("User ID", value="outman")
    project_name = st.text_input("Project name", value="Forge MVP")
    requirements = st.text_area("Requirements", height=160, value="Endpoints + UI wiring")
    submitted = st.form_submit_button("Create project")
    if submitted:
        try:
            created = api.create_project(user_id, project_name, requirements)
            st.success("Project created")
            st.json(created, expanded=False)
            st.session_state["last_created_id"] = created.get("id")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating project: {e}")

st.markdown("---")
st.subheader("Projects")

colA, colB = st.columns([1,1])
with colA:
    if st.button("Refresh list", use_container_width=True):
        st.rerun()
with colB:
    show_raw = st.toggle("Show raw JSON", value=False)

try:
    projects = api.list_projects()
except Exception as e:
    st.error(f"No pude cargar proyectos: {e}")
    projects = []

if not projects:
    st.info("No projects yet.")
else:
    for p in projects:
        pid = p.get("id","")
        pname = p.get("project_name") or p.get("name") or "(unnamed)"
        status = p.get("status","(unknown)")

        with st.container():
            st.write(f"**{pname}**")
            st.caption(f"ID: `{pid}` • Status: **{status}**")

            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                if st.button("Plan", key=f"plan-{pid}"):
                    try:
                        res = api.plan_project(pid)
                        st.toast("Plan started ✓", icon="✅")
                        if isinstance(res, dict) and res.get("job_id"):
                            st.session_state[f"job:{pid}:plan"] = res["job_id"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Plan error: {e}")
            with c2:
                if st.button("Generate", key=f"gen-{pid}"):
                    try:
                        res = api.generate_project(pid)
                        st.toast("Generate started ✓", icon="⚙️")
                        if isinstance(res, dict) and res.get("job_id"):
                            st.session_state[f"job:{pid}:gen"] = res["job_id"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generate error: {e}")
            with c3:
                if st.button("Fetch ZIP", key=f"fetch-{pid}"):
                    try:
                        data, fname = api.fetch_zip(pid)  # descarga vía backend y lo expone localmente
                        st.session_state[f"zip:{pid}"] = (data, fname)
                        st.toast("ZIP listo para descargar", icon="📦")
                    except Exception as e:
                        st.error(f"Download error: {e}")

                res_obj = p.get("result")
                if not isinstance(res_obj, dict):
                    res_obj = {}

                zip_url = res_obj.get("zip_url") or ""
                public_dl = to_public_url(zip_url)
                if public_dl:
                    st.link_button("⬇️ Descargar ZIP", public_dl)

                # Si ya hicimos fetch local, ofrecer descarga directa
                zip_state = st.session_state.get(f"zip:{pid}")
                if zip_state:
                    data, fname = zip_state
                    st.download_button(
                        "Download ZIP (local)",
                        data=data,
                        file_name=fname,
                        mime="application/zip",
                        key=f"dl-{pid}",
                        use_container_width=True,
                    )

            if show_raw:
                st.json(p, expanded=False)
PY
else
  echo "AVISO: ui/app.py no existe; me salto el parche de UI."
fi

echo "==> Reconstruir y arrancar backend + ui"
docker compose up -d --build backend ui

echo "==> Comprobación rápida de salud"
sleep 1
if command -v curl >/dev/null 2>&1; then
  curl -sf http://localhost:8000/api/health >/dev/null && echo "Backend OK"
else
  echo "curl no está en el host, omito test HTTP"
fi

echo "Listo."
