from flask import Blueprint, current_app, render_template, abort
import requests
from app.utils.md import render_markdown_safe

bp = Blueprint("public", __name__)

def api_get(path: str):
    base = current_app.config["API_BASE_URL"].rstrip("/")
    url = f"{base}{path}"
    r = requests.get(url, timeout=10)
    if r.status_code == 404:
        abort(404)
    r.raise_for_status()
    return r.json()

def build_thread(comments: list[dict]) -> list[dict]:
    by_id = {c["id"]: c for c in comments}
    for c in comments:
        c["children"] = []

    roots = []
    for c in comments:
        pid = c.get("parent_comment_id")
        if pid and pid in by_id:
            by_id[pid]["children"].append(c)
        else:
            roots.append(c)
    return roots

@bp.get("/")
def home():
    return render_template("home.html")

@bp.get("/w/<slug>/")
def workspace_home(slug: str):
    posts = api_get(f"/public/w/{slug}/posts")
    return render_template("workspace_home.html", slug=slug, posts=posts)

@bp.get("/w/<slug>/p/<post_slug>/")
def workspace_post(slug: str, post_slug: str):
    post = api_get(f"/public/w/{slug}/posts/{post_slug}")
    comments = api_get(f"/public/w/{slug}/posts/{post_slug}/comments")

    post_html = render_markdown_safe(post.get("body_md", ""))

    for c in comments:
        c["body_html"] = render_markdown_safe(c.get("body", ""))

    threaded = build_thread(comments)

    return render_template(
        "post_detail.html",
        slug=slug,
        post=post,
        post_html=post_html,
        comments_thread=threaded,
    )
