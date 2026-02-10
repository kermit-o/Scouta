from flask import Blueprint, current_app, render_template, request, redirect, session
import requests

bp = Blueprint("admin", __name__)

def api_base() -> str:
    return current_app.config["API_BASE_URL"].rstrip("/")

def api_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def api_post(path: str, token: str | None = None, json_data: dict | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers.update(api_headers(token))
    r = requests.post(f"{api_base()}{path}", json=json_data, headers=headers, timeout=15)
    return r

def api_get(path: str, token: str | None = None):
    headers = {}
    if token:
        headers.update(api_headers(token))
    r = requests.get(f"{api_base()}{path}", headers=headers, timeout=15)
    return r

@bp.get("/admin/login")
def login_form():
    return render_template("admin_login.html", error=None)

@bp.post("/admin/login")
def login_submit():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    org_slug = request.form.get("org_slug", "").strip()

    r = api_post("/auth/login", json_data={"email": email, "password": password})
    if r.status_code != 200:
        return render_template("admin_login.html", error="Invalid credentials"), 401

    token = r.json()["access_token"]

    orgs_resp = api_get("/orgs/me", token=token)
    if orgs_resp.status_code != 200:
        return render_template("admin_login.html", error="Could not load orgs"), 400

    orgs = orgs_resp.json()
    match = next((o for o in orgs if o["slug"] == org_slug), None)
    if not match:
        return render_template("admin_login.html", error="Org slug not found in your account"), 400

    session["token"] = token
    session["org_id"] = match["id"]
    session["org_slug"] = org_slug
    return redirect("/admin")

@bp.get("/admin/logout")
def logout():
    session.clear()
    return redirect("/admin/login")

@bp.get("/admin")
def dashboard():
    token = session.get("token")
    org_id = session.get("org_id")
    org_slug = session.get("org_slug")
    if not token or not org_id:
        return redirect("/admin/login")

    q = api_get(f"/orgs/{org_id}/moderation/queue", token=token)
    actions = q.json() if q.status_code == 200 else []

    p = api_get(f"/orgs/{org_id}/admin/posts?status=published&limit=50", token=token)
    posts = p.json() if p.status_code == 200 else []

    return render_template("admin_dashboard.html", org_slug=org_slug, actions=actions, posts=posts)

@bp.post("/admin/spawn/agents")
def spawn_agents():
    token = session.get("token")
    org_id = session.get("org_id")
    if not token or not org_id:
        return redirect("/admin/login")

    n = int(request.form.get("n", "5"))
    api_post(f"/orgs/{org_id}/agents/spawn?n={n}", token=token)
    return redirect("/admin")

@bp.post("/admin/posts/<int:post_id>/spawn")
def spawn_actions(post_id: int):
    token = session.get("token")
    org_id = session.get("org_id")
    if not token or not org_id:
        return redirect("/admin/login")

    n = int(request.form.get("n", "3"))
    api_post(f"/orgs/{org_id}/posts/{post_id}/spawn-actions?n={n}&force=true", token=token)
    return redirect("/admin")

@bp.post("/admin/moderation/<int:action_id>/approve")
def approve(action_id: int):
    token = session.get("token")
    org_id = session.get("org_id")
    if not token or not org_id:
        return redirect("/admin/login")

    api_post(f"/orgs/{org_id}/moderation/{action_id}/approve", token=token)
    return redirect("/admin")

@bp.post("/admin/moderation/<int:action_id>/reject")
def reject(action_id: int):
    token = session.get("token")
    org_id = session.get("org_id")
    if not token or not org_id:
        return redirect("/admin/login")

    api_post(f"/orgs/{org_id}/moderation/{action_id}/reject", token=token)
    return redirect("/admin")
