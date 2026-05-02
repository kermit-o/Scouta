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
from app.core.deps import require_superuser
from app.models.post import Post
from app.models.user import User
from app.models.org import Org
import app.models  # Para registrar todos los modelos
from app.api.v1 import agent_posts


# Crear tablas si no existen
Base.metadata.create_all(bind=engine, checkfirst=True)

# Auto-add missing columns to live_streams (for Railway where Alembic isn't run manually)
try:
    from sqlalchemy import text as _text, inspect as _inspect
    _conn = engine.connect()
    _existing_cols = {c["name"] for c in _inspect(engine).get_columns("live_streams")}
    _new_cols = {
        "is_private": "BOOLEAN DEFAULT FALSE",
        "password_hash": "VARCHAR(255)",
        "access_type": "VARCHAR(20) DEFAULT 'public'",
        "entry_coin_cost": "INTEGER DEFAULT 0",
        "max_viewer_limit": "INTEGER DEFAULT 0",
    }
    for col_name, col_def in _new_cols.items():
        if col_name not in _existing_cols:
            _conn.execute(_text(f"ALTER TABLE live_streams ADD COLUMN {col_name} {col_def}"))
            print(f"[migrate] added column live_streams.{col_name}")
    # Auto-add withdrawable_balance to coin_wallets
    try:
        _cw_cols = {c["name"] for c in _inspect(engine).get_columns("coin_wallets")}
        if "withdrawable_balance" not in _cw_cols:
            _conn.execute(_text("ALTER TABLE coin_wallets ADD COLUMN withdrawable_balance INTEGER DEFAULT 0"))
            print("[migrate] added column coin_wallets.withdrawable_balance")
    except Exception:
        pass

    # Auto-add payout_method + payout_details to withdrawal_requests
    try:
        _wr_cols = {c["name"] for c in _inspect(engine).get_columns("withdrawal_requests")}
        _wr_new = {
            "payout_method": "VARCHAR(20)",
            "payout_details": "TEXT",
        }
        for col_name, col_def in _wr_new.items():
            if col_name not in _wr_cols:
                _conn.execute(_text(f"ALTER TABLE withdrawal_requests ADD COLUMN {col_name} {col_def}"))
                print(f"[migrate] added column withdrawal_requests.{col_name}")
    except Exception:
        pass

    _conn.commit()
    _conn.close()
except Exception as e:
    print(f"[migrate] auto-migration skipped: {e}")

# Seed gift catalog
try:
    from app.models.gift import seed_gift_catalog
    _seed_db = SessionLocal()
    seed_gift_catalog(_seed_db)
    _seed_db.close()
except Exception as e:
    print(f"[seed] gift catalog seed failed: {e}")

import threading
import time as _time

def _reputation_scheduler():
    """Runs reputation recalc every hour."""
    # Wait 30s after startup before first run
    _time.sleep(30)
    while True:
        try:
            from app.services.reputation_job import run_reputation_job
            run_reputation_job()
        except Exception as e:
            print(f"[reputation_job] error: {e}")
        _time.sleep(3600)  # every hour


# Worker leader election: with multiple gunicorn workers we don't want every
# worker to spawn its own reputation scheduler / agent spawn loop — that
# duplicates AI cost and trips unique constraints on agent_actions.idempotency_key.
# A POSIX flock on a tmp file lets the first worker to start become the leader;
# the others fail to acquire the lock and skip the schedulers.
# Caveat: if the leader crashes the schedulers stop until the next full restart.
_leader_lock_fd = None

def _try_become_leader() -> bool:
    global _leader_lock_fd
    import fcntl
    try:
        _leader_lock_fd = open("/tmp/scouta_bg_leader.lock", "w")
        fcntl.flock(_leader_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except (IOError, OSError):
        if _leader_lock_fd is not None:
            try:
                _leader_lock_fd.close()
            except Exception:
                pass
            _leader_lock_fd = None
        return False


app = FastAPI(
    title="Scouta Blog AI API",
    description="AI-powered blog content generation",
    version="1.0.0"
)

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api/v1")

# CORS
import os

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,"
        "https://serene-eagerness-production.up.railway.app",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup_event():
    """Start background threads only on the leader worker."""
    # Kill switch for the schedulers — set ENABLE_BG_JOBS=false on Railway
    # to stop the spawn_loop / reputation_job without redeploying. Useful
    # when LLM providers are out of credit and logs are being spammed.
    if os.getenv("ENABLE_BG_JOBS", "true").strip().lower() in ("0", "false", "no", "off"):
        print("[startup] ENABLE_BG_JOBS is off — background jobs skipped")
        return
    if not _try_become_leader():
        print(f"[startup] worker pid={os.getpid()} is not leader — background jobs skipped")
        return
    print(f"[startup] worker pid={os.getpid()} is leader — starting background jobs")

    import threading

    # Reputation scheduler
    t1 = threading.Thread(target=_reputation_scheduler, daemon=True)
    t1.start()
    print("[startup] reputation scheduler started")

    # Spawn loop
    def _spawn_loop():
        import time as _t
        _t.sleep(15)
        try:
            from app.jobs.spawn_loop import main as spawn_main
            spawn_main()
        except Exception as e:
            print(f"[spawn_loop] fatal error: {e}")

    t2 = threading.Thread(target=_spawn_loop, daemon=True)
    t2.start()
    print("[startup] spawn loop started")

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

# Manually trigger an AI agent to publish a post. Costs LLM quota,
# so it's gated behind require_superuser to prevent random callers
# from burning DeepSeek/Qwen credits.
@app.post("/api/v1/orgs/{org_id}/generate-post")
async def generate_post(
    org_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """Generar post con DeepSeek (admin only)."""
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
        "SELECT pt.tag FROM post_tags pt "
        "JOIN posts p ON p.id = pt.post_id "
        "WHERE pt.post_id = :post_id AND p.org_id = :org_id AND p.status = 'published' "
        "ORDER BY pt.id LIMIT 5"
    ), {"post_id": post_id, "org_id": org_id}).fetchall()
    return [r[0] for r in rows]


@app.get("/api/v1/orgs/{org_id}/trending-tags")
async def get_trending_tags(org_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text
    rows = db.execute(text(
        "SELECT pt.tag, COUNT(*) as cnt FROM post_tags pt "
        "JOIN posts p ON p.id = pt.post_id "
        "WHERE p.org_id = :org_id AND p.status = 'published' "
        "AND p.created_at > NOW() - INTERVAL '7 days' "
        "GROUP BY pt.tag ORDER BY cnt DESC LIMIT 20"
    ), {"org_id": org_id}).fetchall()
    return [{"tag": r[0], "count": r[1]} for r in rows]


# Public feed of an org. Status param is ignored — always returns published
# posts only, otherwise an unauthenticated caller could pass ?status=draft
# and read unpublished content.
@app.get("/api/v1/orgs/{org_id}/posts")
async def get_posts(org_id: int, db: Session = Depends(get_db), limit: int = 50, tag: str = None, sort: str = "recent"):
    """Obtener posts publicados de una organización (público, solo published)."""
    from sqlalchemy import text as _text
    status = "published"
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
from app.api.v1.debug import router as debug_router
app.include_router(debug_router, prefix="/api/v1")
from app.api.v1.messages import router as messages_router
app.include_router(messages_router, prefix="/api/v1")
app.include_router(agent_posts.router, prefix="/api/v1")
