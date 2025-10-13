
import os, time, requests, streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Forge UI", page_icon="🛠️", layout="centered")
st.title("Forge – Project Builder")

st.sidebar.markdown(f"**Backend**: `{BACKEND_URL}`")
if st.sidebar.button("Health check"):
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=3)
        st.sidebar.success(r.json())
    except Exception as e:
        st.sidebar.error(e)

def show_json(x):
    if isinstance(x, (dict, list)):
        st.json(x)
    elif x is None:
        st.caption("—")
    else:
        st.code(str(x))

with st.form("create_project"):
    user_id = st.text_input("User ID", "outman")
    project_name = st.text_input("Project name", "Forge MVP")
    requirements = st.text_area("Requirements", "Endpoints + UI wiring", height=150)
    submitted = st.form_submit_button("Create project")
    if submitted:
        try:
            r = requests.post(f"{BACKEND_URL}/api/projects", json={
                "user_id": user_id, "project_name": project_name, "requirements": requirements
            }, timeout=10)
            if r.status_code >= 400:
                st.error(r.text)
            else:
                st.success("Project created")
                st.json(r.json())
        except Exception as e:
            st.exception(e)

st.divider()

try:
    projects = requests.get(f"{BACKEND_URL}/api/projects", timeout=5).json()
except Exception as e:
    projects = []
    st.warning(f"Can\"t load projects: {e}")

for p in projects:
    with st.expander(f"📦 {p.get('project_name')} — {p.get('status')} — {p.get('id')}", expanded=False):
        st.code(p.get("requirements") or "")
        c1, c2, c3, c4 = st.columns([1,1,1,1])

        # PLAN
        if c1.button("Generate plan", key=f"plan_{p['id']}"):
            try:
                r = requests.post(f"{BACKEND_URL}/api/projects/{p['id']}/plan", json={}, timeout=10)
                if r.status_code >= 400: st.error(r.text)
                else:
                    job_id = r.json()["job_id"]; prog = st.progress(0); msg = st.empty()
                    while True:
                        pr = requests.get(f"{BACKEND_URL}/api/progress/{job_id}", timeout=5).json()
                        prog.progress(int(pr.get("percent", 0))); msg.write(pr.get("message", ""))
                        if int(pr.get("percent", 0)) >= 100: break
                        time.sleep(1)
                    st.success("Plan ready. Reload to see fields updated.")
            except Exception as e:
                st.exception(e)

        # GENERATE
        if c2.button("Generate app", key=f"gen_{p['id']}"):
            try:
                r = requests.post(f"{BACKEND_URL}/api/projects/{p['id']}/generate", json={}, timeout=10)
                if r.status_code >= 400: st.error(r.text)
                else:
                    job_id = r.json()["job_id"]; prog = st.progress(0); msg = st.empty()
                    while True:
                        pr = requests.get(f"{BACKEND_URL}/api/progress/{job_id}", timeout=5).json()
                        prog.progress(int(pr.get("percent", 0))); msg.write(pr.get("message", ""))
                        if int(pr.get("percent", 0)) >= 100: break
                        time.sleep(1)
                    st.success("Artifact generated. Click refresh below.")
            except Exception as e:
                st.exception(e)

        if c3.button("Refresh", key=f"rf_{p['id']}"):
            st.rerun()

        st.write("**Tech:**"); show_json(p.get("technology_stack"))
        st.write("**Plan:**"); show_json(p.get("generated_plan"))
        st.write("**Result:**")
        res = p.get("result")
        show_json(res)
        if isinstance(res, dict) and res.get("zip_url"):
            st.markdown(f"➡️ **Download:** [{p['project_name']}.zip]({BACKEND_URL}{res['zip_url']})")

