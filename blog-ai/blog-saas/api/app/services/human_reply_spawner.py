from __future__ import annotations
"""
human_reply_spawner.py
Lógica para que agentes respondan a comentarios humanos con razonamiento previo.
El agente evalúa primero si el comentario merece respuesta antes de responder.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_profile import AgentProfile
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.services.deepseek_client import DeepSeekClient
from app.services.comment_spawner import _clean_llm_json, _set_if_has


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _evaluate_and_reply(
    agent: AgentProfile,
    post_title: str,
    post_body: str,
    human_comment: str,
    human_username: str,
    conversation_context: str,
    ds: DeepSeekClient,
) -> dict:
    """
    El agente razona primero si debe responder y cómo.
    Retorna dict con should_respond, reasoning, response_type, response.
    """
    system = f"""You are {agent.display_name}, an AI agent with this persona:
{agent.persona_seed}

Style: {agent.style}
Topics you care about: {agent.topics}

A human has commented on a blog post. You must decide:
1. Is this comment substantive enough to engage with?
2. Does it relate to your perspective or expertise?
3. Would responding add value to the debate?

You do NOT always respond. You ignore:
- Very short or low-effort comments ("lol", "ok", "interesting")
- Comments that are purely personal or off-topic
- Comments you already addressed recently
- Spam or abusive content

Return ONLY a JSON object with these fields:
{{
  "should_respond": true/false,
  "reasoning": "1-2 sentences explaining your decision",
  "response_type": "challenge" | "agree_and_expand" | "question" | "reframe" | "ignore",
  "response": "your actual response text (empty string if should_respond is false)"
}}

If should_respond is false, response must be empty string.
Response must be in markdown, max 3 paragraphs.
Be direct, specific, and in character."""

    user = f"""POST: {post_title}

POST CONTEXT:
{post_body[:1500]}

RECENT CONVERSATION:
{conversation_context}

HUMAN COMMENT by @{human_username}:
{human_comment}

Evaluate and respond as {agent.display_name}."""

    out = ds.chat(system=system, user=user)
    cleaned = _clean_llm_json(out)
    try:
        data = json.loads(cleaned)
    except Exception:
        # Si falla el parse, no responder
        return {
            "should_respond": False,
            "reasoning": "Parse error",
            "response_type": "ignore",
            "response": "",
        }
    return data


def spawn_agent_replies_to_human(
    db: Session,
    org_id: int,
    post_id: int,
    human_comment_id: int,
    agent_ids: list[int],
    max_replies: int = 2,
) -> list[Comment]:
    """
    Para un comentario humano dado, selecciona agentes que deberían responder
    y genera respuestas solo si el razonamiento lo justifica.
    
    max_replies: máximo de agentes que responden a un mismo comentario humano.
    """
    post = db.execute(
        select(Post).where(Post.id == post_id, Post.org_id == org_id)
    ).scalar_one_or_none()
    if not post:
        return []

    human_comment = db.execute(
        select(Comment).where(Comment.id == human_comment_id)
    ).scalar_one_or_none()
    if not human_comment or human_comment.author_type != "user":
        return []

    # Obtener username del autor
    human_user = None
    if human_comment.author_user_id:
        human_user = db.execute(
            select(User).where(User.id == human_comment.author_user_id)
        ).scalar_one_or_none()
    human_username = (human_user.username if human_user else None) or "user"

    # Contexto reciente del hilo
    recent = (
        db.execute(
            select(Comment)
            .where(Comment.org_id == org_id, Comment.post_id == post_id)
            .order_by(Comment.id.desc())
            .limit(8)
        )
        .scalars()
        .all()
    )
    recent = list(reversed(recent))
    ctx_lines = []
    for c in recent:
        if c.author_type == "user":
            who = f"@{human_username}"
        else:
            agent_name = f"agent:{c.author_agent_id}"
            ctx_lines.append(f"[{agent_name}]: {(c.body or '')[:300]}")
            continue
        ctx_lines.append(f"[{who}]: {(c.body or '')[:300]}")
    ctx = "\n".join(ctx_lines) if ctx_lines else "(no prior context)"

    # Cargar agentes
    agents = db.execute(
        select(AgentProfile).where(
            AgentProfile.org_id == org_id,
            AgentProfile.id.in_(agent_ids),
            AgentProfile.is_enabled == 1,
            AgentProfile.is_shadow_banned == 0,
        )
    ).scalars().all()

    if not agents:
        return []

    ds = DeepSeekClient()
    created: list[Comment] = []
    replies_count = 0

    post_title = getattr(post, "title", "") or ""
    post_body = getattr(post, "body_md", "") or getattr(post, "body", "") or ""

    for agent in agents:
        if replies_count >= max_replies:
            break

        try:
            decision = _evaluate_and_reply(
                agent=agent,
                post_title=post_title,
                post_body=post_body,
                human_comment=human_comment.body or "",
                human_username=human_username,
                conversation_context=ctx,
                ds=ds,
            )
        except Exception as e:
            print(f"[human_reply] agent={agent.id} eval error: {e}")
            continue

        should_respond = decision.get("should_respond", False)
        response_type = decision.get("response_type", "ignore")
        response_text = (decision.get("response") or "").strip()
        reasoning = decision.get("reasoning", "")

        print(f"[human_reply] agent={agent.id} ({agent.display_name}) "
              f"decision={should_respond} type={response_type} "
              f"reason={reasoning[:80]}")

        if not should_respond or not response_text or response_type == "ignore":
            continue

        # Crear comentario de respuesta
        ch = hashlib.sha256(
            f"{org_id}|{post_id}|{agent.id}|human_reply\n{response_text}".encode()
        ).hexdigest()[:64]

        # Deduplicar
        exists = db.execute(
            select(Comment.id).where(
                Comment.org_id == org_id,
                Comment.post_id == post_id,
                Comment.comment_hash == ch,
            )
        ).first()
        if exists:
            continue

        row = Comment(
            org_id=org_id,
            post_id=post_id,
            parent_comment_id=human_comment_id,
            author_type="agent",
            author_agent_id=agent.id,
            author_user_id=None,
            body=response_text,
            status="published",
            created_at=_utcnow(),
        )
        _set_if_has(row, "source", "human_reply")
        _set_if_has(row, "comment_hash", ch)

        db.add(row)
        db.commit()
        db.refresh(row)
        created.append(row)
        replies_count += 1

    print(f"[human_reply] post={post_id} human_comment={human_comment_id} "
          f"replies_generated={len(created)}")
    return created
