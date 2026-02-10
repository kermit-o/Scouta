from pathlib import Path

import sqlalchemy as sa
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.org import Org
from app.models.post import Post
from app.models.comment import Comment

router = APIRouter()

@router.get("/blog", response_class=HTMLResponse, include_in_schema=False, name="public_global_feed")
def public_global_feed(request: Request, page: int = 1, per_page: int = 20):
    """
    Global feed: latest posts across all orgs.
    Uses DB introspection to filter published content if columns exist.
    """
    page = max(1, int(page))
    per_page = max(1, min(100, int(per_page)))
    offset = (page - 1) * per_page

    db = SessionLocal()
    try:
        insp = sa.inspect(db.bind)
        posts_cols = {c["name"] for c in insp.get_columns("posts")}
        where = []
        # Prefer status if present; otherwise published_at if present
        if "status" in posts_cols:
            where.append("p.status = 'published'")
        elif "published_at" in posts_cols:
            where.append("p.published_at IS NOT NULL")

        sql = """
        SELECT
            p.id AS post_id,
            p.slug AS post_slug,
            p.title AS post_title,
            p.org_id AS org_id,
            o.slug AS org_slug,
            o.name AS org_name
        FROM posts p
        JOIN orgs o ON o.id = p.org_id
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY p.id DESC LIMIT :limit OFFSET :offset"

        rows = db.execute(sa.text(sql), {"limit": per_page, "offset": offset}).mappings().all()
        posts = [dict(r) for r in rows]

        return templates.TemplateResponse(
            "public_feed.html",
            {
                "request": request,
                "posts": posts,
                "page": page,
                "per_page": per_page,
            },
        )
    finally:
        db.close()



@router.get("/blog/{handle}")
def public_home(request: Request):
    db = _db()
    try:
        # latest published posts across orgs
        posts_q = (
            db.query(Post, Org)
            .join(Org, Org.id == Post.org_id)
            .filter(Post.status == "published")
            .order_by(Post.published_at.desc(), Post.created_at.desc())
            .limit(30)
            .all()
        )
        posts = []
        for post, org in posts_q:
            posts.append({
                "title": post.title,
                "slug": post.slug,
                "created_at": getattr(post, "created_at", None),
                "published_at": getattr(post, "published_at", None),
                "org_name": org.name,
                "org_slug": org.slug,
            })

        return templates.TemplateResponse(
            "public_home.html",
            {"request": request, "posts": posts, "handle": "Global Feed"},
        )
    finally:
        db.close()


TEMPLATES_DIR = str(Path(__file__).resolve().parents[3] / "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def _db() -> Session:
    return SessionLocal()

def _comment_text(c: Comment) -> str:
    # Support both "body" or "content" without crashing
    return (getattr(c, "body", None) or getattr(c, "content", None) or "").strip()

@router.get("/blog/{org_slug}/{post_slug}", response_class=HTMLResponse)
def public_blog_post(org_slug: str, post_slug: str, request: Request):
    """Public post page: /blog/{org_slug}/{post_slug}"""
    db = SessionLocal()
    try:
        org = db.query(Org).filter(Org.slug == org_slug).one_or_none()
        if org is None:
            return HTMLResponse("Not found", status_code=404)

        q = db.query(Post).filter(Post.org_id == org.id, Post.slug == post_slug)
        if hasattr(Post, "status"):
            q = q.filter(Post.status == "published")
        post = q.one_or_none()
        if post is None:
            return HTMLResponse("Not found", status_code=404)

        # comments are optional (model may or may not exist)
        comments = []
        try:
            from app.models.comment import Comment  # type: ignore
            qc = db.query(Comment).filter(Comment.post_id == post.id)
            if hasattr(Comment, "status"):
                qc = qc.filter(Comment.status == "published")
            if hasattr(Comment, "created_at"):
                qc = qc.order_by(Comment.created_at.asc())
            comments = qc.all()
        except Exception:
            comments = []

        # Prefer templates if present; otherwise fall back to simple HTML
        try:
            return templates.TemplateResponse(
                "public_post.html",
                {"request": request, "org": org, "post": post, "comments": comments},
            )
        except Exception:
            title = getattr(post, "title", post_slug)
            body = getattr(post, "body_md", "")
            return HTMLResponse(f"<h1>{title}</h1><pre>{body}</pre>", status_code=200)
    finally:
        db.close()

@router.get("/blog/{handle}")
def public_blog_home(handle: str, request: Request):
    # List latest published posts for this handle (public home)
    db = SessionLocal()
    try:
        # Try common patterns: Org/AgentProfile handle -> posts
        # Prefer OrgSettings/org handle if model exists; fallback to posts by org_id resolved from handle.
        org = db.query(Org).filter(Org.slug == handle).one_or_none()
        if org is None:
            # Some builds store handle on Org.name/handle; try those if present
            for field in ("handle", "name"):
                if hasattr(Org, field):
                    org = db.query(Org).filter(getattr(Org, field) == handle).one_or_none()
                    if org:
                        break

        posts = []
        if org is not None:
            q = db.query(Post).filter(Post.org_id == org.id)
            if hasattr(Post, "status"):
                q = q.filter(Post.status == "published")
            if hasattr(Post, "published_at"):
                q = q.order_by(Post.published_at.desc())
            posts = q.limit(20).all()

        return templates.TemplateResponse(
            "public_home.html",
            {"request": request, "handle": handle, "posts": posts},
        )
    finally:
        db.close()

@router.get("/blog-health")
def blog_health():
    return {"ok": True, "service": "public_blog"}
