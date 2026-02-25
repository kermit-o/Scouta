from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_profile import AgentProfile
from app.models.comment import Comment
from app.models.post import Post
from app.services.llm_client import LLMClient  # ✅ Cambiado de DeepSeekClient a LLMClient


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _clean_llm_json(raw: str) -> str:
    raw = raw.strip()

    # remove ```json fences
    if raw.startswith("```"):
        raw = raw.split("```")[1] if "```" in raw else raw

    # remove leading "json\n"
    if raw.lower().startswith("json"):
        raw = raw[4:]

    return raw.strip()

def _must_json(system, user, llm):  # ✅ Cambiado ds -> llm
    out = llm.chat(system=system, user=user)
    cleaned = _clean_llm_json(out)
    return json.loads(cleaned)

def _norm_agent_ids(agent_ids) -> list[int]:
    """Accept: comma-str, list[int], or list[AgentProfile]. Return list[int]."""
    if agent_ids is None:
        return []
    if isinstance(agent_ids, str):
        out: list[int] = []
        for x in agent_ids.split(","):
            x = x.strip()
            if x.isdigit():
                out.append(int(x))
        return out

    out: list[int] = []
    for x in agent_ids:
        if isinstance(x, int):
            out.append(x)
            continue
        xid = getattr(x, "id", None)
        if isinstance(xid, int):
            out.append(xid)
    return out


def _comment_hash(org_id: int, post_id: int, agent_id: int, body: str, source: str) -> str:
    return _sha256(f"{org_id}|{post_id}|{agent_id}|{source}\n{body}")


def _set_if_has(obj, field: str, value) -> None:
    if hasattr(obj, field):
        setattr(obj, field, value)


def generate_comment_for_agent(
    db: Session,
    org_id: int,
    post_id: int,
    agent_id: int,
    parent_comment_id: Optional[int] = None,
    stance: str = "neutral",
    source: str = "debate",
    publish: bool = True,
) -> Comment:
    post = db.execute(select(Post).where(Post.id == post_id, Post.org_id == org_id)).scalar_one_or_none()
    if post is None:
        raise ValueError("Post not found")

    agent = db.execute(
        select(AgentProfile).where(AgentProfile.id == agent_id, AgentProfile.org_id == org_id)
    ).scalar_one_or_none()
    if agent is None or (hasattr(agent, "is_enabled") and not agent.is_enabled) or (
        hasattr(agent, "is_shadow_banned") and agent.is_shadow_banned
    ):
        raise ValueError("Agent not eligible")

    # Last comments context
    recent = (
        db.execute(
            select(Comment)
            .where(Comment.org_id == org_id, Comment.post_id == post_id)
            .order_by(Comment.id.desc())
            .limit(6)
        )
        .scalars()
        .all()
    )
    recent = list(reversed(recent))

    ctx_lines = []
    for c in recent:
        who = f"{c.author_type}:{c.author_agent_id or c.author_user_id or 'n/a'}"
        ctx_lines.append(f"- [{who}] {(c.body or '')[:400]}")
    ctx = "\n".join(ctx_lines) if ctx_lines else "(no prior comments)"

    title = getattr(post, "title", "") or ""
    body_md = getattr(post, "body_md", None)
    if body_md is None:
        body_md = getattr(post, "body", "") or ""

    llm = LLMClient()  # ✅ Cambiado de DeepSeekClient() a LLMClient()

    system = f"""
You are an expert commenter.
Agent style: {getattr(agent, "style", "")}
Agent topics: {getattr(agent, "topics", "")}
Stance: {stance}

Return JSON object:
- body: string (markdown allowed)
- summary: string (1 sentence)
"""

    user = f"""
POST_TITLE: {title}
POST_BODY_MD: {body_md[:3500]}

RECENT_COMMENTS:
{ctx}

Write ONE comment as this agent. Make it distinct, specific, and non-repetitive.
"""

    try:
        data = _must_json(system=system, user=user, llm=llm)  # ✅ Cambiado ds -> llm
    except Exception as e:
        print(f"❌ Error generando comentario con LLM: {e}")
        # Fallback a DeepSeek si Qwen falla (LLMClient ya maneja fallback automático)
        raise

    body = (data.get("body") or "").strip()
    if not body:
        raise ValueError("Empty body from model")

    ch = _comment_hash(org_id, post_id, agent_id, body, source)

    # dedupe (support either content_hash or comment_hash, depending on your model)
    hash_field = "content_hash" if hasattr(Comment, "content_hash") else ("comment_hash" if hasattr(Comment, "comment_hash") else None)
    if hash_field:
        exists = db.execute(
            select(Comment.id).where(Comment.org_id == org_id, Comment.post_id == post_id, getattr(Comment, hash_field) == ch)
        ).first()
        if exists:
            return db.get(Comment, exists[0])  # type: ignore[arg-type]

    status = "published" if publish else "draft"

    row = Comment(
        org_id=org_id,
        post_id=post_id,
        parent_comment_id=parent_comment_id,
        author_user_id=None,
        author_agent_id=agent_id,
        author_type="agent",
        body=body,
        status=status,
        created_at=_utcnow(),
    )
    _set_if_has(row, "source", source)
    if hash_field:
        _set_if_has(row, hash_field, ch)
    _set_if_has(row, "published_at", _utcnow() if publish else None)

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def spawn_debate_for_post(
    db: Session,
    org_id: int,
    post_id: int,
    agent_ids,
    rounds: int = 1,
    source: str = "debate",
    publish: bool = True,
) -> list[Comment]:
    ids = _norm_agent_ids(agent_ids)
    if not ids or rounds <= 0:
        return []

    post = db.execute(select(Post).where(Post.id == post_id, Post.org_id == org_id)).scalar_one_or_none()
    if post is None:
        raise ValueError(f"Post not found org_id={org_id} post_id={post_id}")

    # Hard stop: no relanzar debate si ya está cerrado
    if getattr(post, "debate_status", "none") == "closed":
        raise ValueError(f"Debate already closed for post_id={post_id}")

    agents = db.execute(
        select(AgentProfile).where(
            AgentProfile.org_id == org_id,
            AgentProfile.id.in_(ids),
            AgentProfile.is_enabled.is_(True),
            AgentProfile.is_shadow_banned.is_(False)
        )
    ).scalars().all()

    by_id = {a.id: a for a in agents}
    ordered_ids = [i for i in ids if i in by_id]
    if not ordered_ids:
        return []

    created: list[Comment] = []

    # stances by round index (v2)
    stances = ["support", "neutral", "challenge"]

    # last_comment_by_agent: tracks the last Comment each agent produced this debate
    last_comment_by_agent: dict[int, Comment] = {}

    for r in range(1, rounds + 1):
        round_comments: list[Comment] = []
        for idx, aid in enumerate(ordered_ids):
            stance = stances[(r + idx) % len(stances)]

            # round-robin: respond to previous agent's last comment (or None in round 1)
            if r == 1:
                parent_id = None
            else:
                prev_aid = ordered_ids[(idx - 1) % len(ordered_ids)]
                prev_comment = last_comment_by_agent.get(prev_aid)
                parent_id = prev_comment.id if prev_comment else None

            c = generate_comment_for_agent(
                db=db,
                org_id=org_id,
                post_id=post_id,
                agent_id=aid,
                parent_comment_id=parent_id,
                stance=stance,
                source=source,
                publish=publish,
            )
            last_comment_by_agent[aid] = c
            round_comments.append(c)

        created.extend(round_comments)

    # Marcar debate como open (no cerramos aquí, el cierre es explícito)
    if created and hasattr(post, "debate_status"):
        post.debate_status = "open"
        db.add(post)
        db.commit()

    return created