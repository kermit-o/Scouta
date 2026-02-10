from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.core.db import SessionLocal
from app.models.post import Post
from app.models.org_settings import OrgSettings
from app.services.action_spawner import spawn_actions_for_post


@dataclass
class AutoState:
    enabled: bool = False
    started_at: str | None = None
    last_tick_at: str | None = None
    last_error: str | None = None
    ticks: int = 0
    spawns: int = 0


STATE = AutoState()
_LOCK = threading.Lock()
_THREAD: threading.Thread | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _get_env_bool(name: str, default: str = "false") -> bool:
    v = os.getenv(name, default).strip().lower()
    return v in ("1", "true", "yes", "on")


def _get_env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def _get_env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default


def start_scheduler_if_enabled() -> None:
    global _THREAD
    enabled = _get_env_bool("AUTO_MODE_ENABLED", "false")
    with _LOCK:
        STATE.enabled = enabled

    if not enabled:
        return

    if _THREAD and _THREAD.is_alive():
        return

    _THREAD = threading.Thread(target=_run_loop, name="auto-mode", daemon=True)
    _THREAD.start()
    with _LOCK:
        STATE.started_at = _iso(_utc_now())


def snapshot() -> dict:
    with _LOCK:
        return {
            "enabled": STATE.enabled,
            "started_at": STATE.started_at,
            "last_tick_at": STATE.last_tick_at,
            "last_error": STATE.last_error,
            "ticks": STATE.ticks,
            "spawns": STATE.spawns,
        }


def _run_loop() -> None:
    interval_s = _get_env_int("AUTO_MODE_INTERVAL_SECONDS", 120)

    while True:
        try:
            _tick()
            time.sleep(interval_s)
        except Exception as e:
            with _LOCK:
                STATE.last_error = f"{type(e).__name__}: {e}"
            # backoff
            time.sleep(min(interval_s * 2, 600))


def _tick() -> None:
    org_id = _get_env_int("AUTO_MODE_ORG_ID", 1)
    max_posts = _get_env_int("AUTO_MODE_MAX_POSTS_PER_TICK", 3)
    actions_per_post = _get_env_int("AUTO_MODE_ACTIONS_PER_POST", 1)
    base_prob = _get_env_float("AUTO_MODE_SPAWN_PROBABILITY", 0.35)
    min_age_min = _get_env_int("AUTO_MODE_MIN_POST_AGE_MINUTES", 2)

    db = SessionLocal()
    try:
        settings = db.query(OrgSettings).filter(OrgSettings.org_id == org_id).one_or_none()
        if settings and hasattr(settings, "agents_enabled") and not settings.agents_enabled:
            _mark_tick()
            return

        cutoff = _utc_now() - timedelta(minutes=min_age_min)
        posts = (
            db.query(Post)
            .filter(Post.org_id == org_id)
            .filter(Post.status == "published")
            .order_by(Post.published_at.desc())
            .limit(25)
            .all()
        )

        # Pick candidates that are older than cutoff (avoid immediate spam right after publish)
        candidates = []
        for p in posts:
            # published_at might be naive; treat as UTC naive
            pub = p.published_at or p.created_at
            if not pub:
                continue
            if pub.tzinfo is None:
                pub_dt = pub.replace(tzinfo=timezone.utc)
            else:
                pub_dt = pub.astimezone(timezone.utc)
            if pub_dt <= cutoff:
                candidates.append(p)

        random.shuffle(candidates)
        selected = candidates[:max_posts]

        spawned = 0
        for p in selected:
            # Probabilistic spawn per post (base_prob)
            if random.random() > base_prob:
                continue
            out = spawn_actions_for_post(
                db,
                org_id=org_id,
                post_id=p.id,
                max_n=actions_per_post,
                force=True,
            )
            spawned += len(out or [])

        with _LOCK:
            STATE.spawns += spawned

        _mark_tick()

    except Exception as e:
        with _LOCK:
            STATE.last_error = f"{type(e).__name__}: {e}"
        _mark_tick()
        raise
    finally:
        db.close()


def _mark_tick() -> None:
    with _LOCK:
        STATE.ticks += 1
        STATE.last_tick_at = _iso(_utc_now())

# Agregar al final del archivo, antes de las funciones de scheduling
from app.services.post_generator import PostGenerator
from app.models.agent_profile import AgentProfile

def _create_posts_from_trends(db):
    """
    Crea posts automáticamente desde tendencias
    """
    from app.services.post_generator import PostGenerator
    
    # Obtener organización en auto-mode
    org_id = int(os.getenv("AUTO_MODE_ORG_ID", "1"))
    
    # Obtener agentes activos
    agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.is_enabled == True
    ).all()
    
    if not agents:
        print("No hay agentes activos para generar posts")
        return
    
    agent_ids = [agent.id for agent in agents]
    
    # Crear posts (1-2 por tick)
    import random
    num_posts = random.randint(1, 2)
    
    generator = PostGenerator(db)
    posts = generator.generate_multiple_posts(org_id, agent_ids, num_posts)
    
    print(f"Generados {len(posts)} posts desde tendencias")
    
    # Programar comentarios automáticos para estos nuevos posts
    for post in posts:
        if random.random() < 0.7:  # 70% probabilidad
            from app.services.action_spawner import spawn_actions_for_post
            n_comments = random.randint(1, 3)
            try:
                spawn_actions_for_post(db, post.org_id, post.id, n_comments, force=False)
                print(f"  Programados {n_comments} comentarios para post #{post.id}")
            except Exception as e:
                print(f"  Error programando comentarios: {e}")

# Modificar la función _tick para incluir creación de posts
# Buscar la función _tick y agregar llamada a _create_posts_from_trends
