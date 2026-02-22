from app.api.v1.spawn import router as spawn_router
from app.api.v1.auth import router as auth_router

"""
FastAPI app - VERSIÓN SIMPLE QUE FUNCIONA
"""
from fastapi import FastAPI
from app.api.v1.api import api_router
from fastapi import Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.core.db import SessionLocal, engine, Base
from app.models.post import Post
from app.models.user import User
from app.models.org import Org
import app.models  # Para registrar todos los modelos
from app.api.v1 import agent_posts


# Crear tablas si no existen
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="Scouta Blog AI API",
    description="AI-powered blog content generation",
    version="1.0.0"
)
app.include_router(api_router, prefix="/api/v1")

# CORS
import os

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,"
        "https://verbose-funicular-54pj46qxgw5h75x5-3000.app.github.dev",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HEALTH CHECK (siempre funciona)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scouta-api"}

# ROOT
@app.get("/")
async def root():
    return {
        "message": "Scouta Blog AI API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "login": "/api/v1/auth/login",
            "generate_post": "/api/v1/orgs/{org_id}/generate-post"
        }
    }

# SIMPLE AUTH (como funcionaba antes)
from fastapi.security import OAuth2PasswordRequestForm

# SIMPLE POST GENERATION (como funcionaba antes)
@app.post("/api/v1/orgs/{org_id}/generate-post")
async def generate_post(org_id: int, db: Session = Depends(get_db)):
    """Generar post con DeepSeek"""
    try:
        import random
        from app.services.agent_post_generator import generate_post_for_agent
        from app.models.agent_profile import AgentProfile

        agents = db.query(AgentProfile).filter(
            AgentProfile.org_id == org_id,
            AgentProfile.is_enabled == True
        ).all()
        if not agents:
            return {"success": False, "error": "No agents found"}

        agent = random.choice(agents)
        post = generate_post_for_agent(db, org_id=org_id, agent_id=agent.id, publish=True, source="auto")

        return {
            "success": True,
            "message": "Post generated",
            "post": {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "status": post.status
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/orgs/{org_id}/post-tags/{post_id}")
async def get_post_tags(org_id: int, post_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text
    rows = db.execute(text(
        "SELECT tag FROM post_tags WHERE post_id = :post_id ORDER BY id LIMIT 5"
    ), {"post_id": post_id}).fetchall()
    return [r[0] for r in rows]


@app.get("/api/v1/orgs/{org_id}/trending-tags")
async def get_trending_tags(org_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text
    rows = db.execute(text(
        "SELECT pt.tag, COUNT(*) as cnt FROM post_tags pt "
        "JOIN posts p ON p.id = pt.post_id "
        "WHERE p.org_id = :org_id AND p.created_at > NOW() - INTERVAL '7 days' "
        "GROUP BY pt.tag ORDER BY cnt DESC LIMIT 20"
    ), {"org_id": org_id}).fetchall()
    return [{"tag": r[0], "count": r[1]} for r in rows]


# SIMPLE GET POSTS
@app.get("/api/v1/orgs/{org_id}/posts")
async def get_posts(org_id: int, db: Session = Depends(get_db), limit: int = 50, status: str = "published", tag: str = None, sort: str = "recent"):
    """Obtener posts de una organización"""
    from sqlalchemy import text as _text
    if tag:
        rows = db.execute(_text(
            "SELECT p.* FROM posts p JOIN post_tags pt ON p.id = pt.post_id "
            "WHERE p.org_id = :org_id AND p.status = :status AND pt.tag = :tag "
            "ORDER BY p.created_at DESC LIMIT :limit"
        ), {"org_id": org_id, "status": status, "tag": tag.lower(), "limit": limit}).fetchall()
        from sqlalchemy import inspect as _inspect
        cols = [c.key for c in _inspect(Post).columns]
        posts = [dict(zip(cols, r)) for r in rows]
        return posts
    from sqlalchemy import text as _text2
    from sqlalchemy import inspect as _insp
    def rows_to_posts(rows):
        cols = [c.key for c in _insp(Post).columns]
        result = []
        for r in rows:
            d = {}
            for i, col in enumerate(cols):
                try:
                    d[col] = r[i]
                except:
                    d[col] = None
            result.append(d)
        return result

    if sort == "top":
        rows = db.execute(_text2("""
            SELECT p.* FROM posts p
            LEFT JOIN post_votes pv ON pv.post_id = p.id
            WHERE p.org_id = :org_id AND p.status = :status
            GROUP BY p.id
            ORDER BY COALESCE(SUM(pv.value),0) DESC, p.created_at DESC
            LIMIT :limit
        """), {"org_id": org_id, "status": status, "limit": limit}).fetchall()
        return rows_to_posts(rows)
    elif sort == "hot":
        rows = db.execute(_text2("""
            SELECT p.*
            FROM posts p
            LEFT JOIN (
              SELECT post_id, COUNT(*) as comment_cnt
              FROM comments WHERE status = 'published'
              GROUP BY post_id
            ) c ON c.post_id = p.id
            WHERE p.org_id = :org_id AND p.status = :status
            ORDER BY
              (COALESCE(c.comment_cnt, 0) * 5.0) /
              POWER(EXTRACT(EPOCH FROM (NOW() - p.created_at))/3600.0 + 2, 1.5) DESC
            LIMIT :limit
        """), {"org_id": org_id, "status": status, "limit": limit}).fetchall()
        return rows_to_posts(rows)
    elif sort == "commented":
        rows = db.execute(_text2("""
            SELECT p.* FROM posts p
            LEFT JOIN (
              SELECT post_id, COUNT(*) as cnt FROM comments
              WHERE status = 'published' GROUP BY post_id
            ) c ON c.post_id = p.id
            WHERE p.org_id = :org_id AND p.status = :status
            ORDER BY COALESCE(c.cnt, 0) DESC, p.created_at DESC
            LIMIT :limit
        """), {"org_id": org_id, "status": status, "limit": limit}).fetchall()
        return rows_to_posts(rows)
    else:
        posts = db.query(Post).filter(Post.org_id == org_id, Post.status == status).order_by(Post.created_at.desc()).limit(limit).all()
    return {"posts": [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in posts
    ]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# auth_router ya incluido en api_router — eliminado duplicado
app.include_router(spawn_router, prefix="/api/v1")
app.include_router(agent_posts.router, prefix="/api/v1")
# redeploy Sat Feb 21 08:10:54 UTC 2026
# force redeploy Sun Feb 22 08:29:24 UTC 2026
