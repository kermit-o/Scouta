import hashlib
import os
import random
from datetime import datetime, timezone, date, timedelta


def _make_idempotency_key(org_id: int, post_id: int, n: int, force: bool) -> str:
    # stable + deterministic for the same request intent
    return f"spawn:org={org_id}:post={post_id}:n={n}:force={int(force)}"
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from app.models.agent_profile import AgentProfile
from app.models.agent_action import AgentAction
from app.models.org_settings import OrgSettings
from app.models.agent_policy import AgentPolicy
from app.models.post import Post
from app.models.comment import Comment
from app.models.org_usage_daily import OrgUsageDaily
from app.services.persona_writer import Persona, write_comment
from app.services.moderation_scorer import score_text_with_deepseek

def _materialize_published_comment_action(db, action) -> None:
    """
    If action is a published 'comment' action, create a real Comment row (idempotent).
    Supports:
      - target_type='post'   -> creates top-level comment on that post
      - target_type='comment'-> creates reply to an existing comment
    """
    if getattr(action, "action_type", None) != "comment":
        return
    if getattr(action, "status", None) != "published":
        return
    body = (getattr(action, "content", None) or "").strip()
    if not body:
        return

    parent_comment_id = None
    post_id = None

    if getattr(action, "target_type", None) == "post":
        post_id = int(action.target_id)
    elif getattr(action, "target_type", None) == "comment":
        parent = db.query(Comment).filter(Comment.id == int(action.target_id)).one_or_none()
        if not parent:
            return
        post_id = int(parent.post_id)
        parent_comment_id = int(parent.id)
    else:
        return

    # Idempotency: avoid duplicates if same agent posted same body on same post
    exists = (
        db.query(Comment)
          .filter(Comment.post_id == post_id)
          .filter(Comment.author_type == "agent")
          .filter(Comment.author_agent_id == int(action.agent_id))
          .filter(Comment.body == body)
          .one_or_none()
    )
    if exists:
        return

    c = Comment(
        org_id=int(action.org_id),
        post_id=post_id,
        parent_comment_id=parent_comment_id,
        author_type="agent",
        author_user_id=None,
        author_agent_id=int(action.agent_id),
        body=body,
        status="published",
    )
    db.add(c)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # if unique index exists, fetch existing by idempotency_key
        # Note: creation of Comment succeeded, idempotency is handled by the unique query above
        pass  # TODO: Revisar lógica de idempotencia aquí


def _idempotency_key(*parts: str) -> str:
    """Stable idempotency key: sha256 hex."""
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()

def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _get_or_create_usage(db: Session, org_id: int) -> OrgUsageDaily:
    d = _today_utc()
    row = (
        db.query(OrgUsageDaily)
        .filter(OrgUsageDaily.org_id == org_id, OrgUsageDaily.day_utc == d)
        .one_or_none()
    )
    if row:
        return row
    row = OrgUsageDaily(org_id=org_id, day_utc=d, actions_spawned=0, actions_published=0)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row



def _enforce_org_quotas(db, org_settings, org_id: int) -> None:
    # agents_enabled
    if hasattr(org_settings, "agents_enabled") and (not org_settings.agents_enabled):
        raise ValueError("Agents disabled")

    # max_actions_per_day
    max_per_day = getattr(org_settings, "max_actions_per_day", None)
    if max_per_day:
        from app.models.agent_action import AgentAction  # local import to avoid cycles
        # count actions in last 24h
        since = datetime.utcnow() - timedelta(days=1)
        cnt = (
            db.query(AgentAction)
            .filter(AgentAction.org_id == org_id)
            .filter(AgentAction.created_at >= since)
            .count()
        )
        if cnt >= int(max_per_day):
            raise ValueError(f"Daily actions quota reached ({cnt}/{max_per_day})")

def _enforce_post_agent_cap(db, org_settings, org_id: int, post_id: int) -> None:
    cap = getattr(org_settings, "max_agents_per_post", None)
    if not cap:
        return
    from app.models.agent_action import AgentAction
    # count distinct agents that already produced actions for this post
    rows = (
        db.query(AgentAction.agent_id)
        .filter(AgentAction.org_id == org_id)
        .filter(AgentAction.target_type == "post")
        .filter(AgentAction.target_id == post_id)
        .distinct()
        .all()
    )
    if len(rows) >= int(cap):
        raise ValueError(f"max_agents_per_post reached ({len(rows)}/{cap})")



from datetime import datetime, timedelta

IDEMPOTENCY_WINDOW_SECONDS = 120

def _is_duplicate_action(db, *, org_id: int, post_id: int, agent_id: int, action_type: str):
    """Return existing action if duplicated recently."""
    cutoff = datetime.utcnow() - timedelta(seconds=IDEMPOTENCY_WINDOW_SECONDS)
    return (
        db.query(AgentAction)
        .filter(
            AgentAction.org_id == org_id,
            AgentAction.target_type == "post",
            AgentAction.target_id == post_id,
            AgentAction.agent_id == agent_id,
            AgentAction.action_type == action_type,
            AgentAction.status == "published",
            AgentAction.created_at >= cutoff,
        )
        .order_by(AgentAction.created_at.desc())
        .first()
    )


def spawn_actions_for_post(db: Session, org_id: int, post_id: int, max_n: int, force: bool = False, idempotency_key: str | None = None) -> list[AgentAction]:
    settings = db.query(OrgSettings).filter(OrgSettings.org_id == org_id).one_or_none()
    if not settings:
        settings = OrgSettings(org_id=org_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    policy = db.query(AgentPolicy).filter(AgentPolicy.org_id == org_id).one_or_none()
    if not policy:
        policy = AgentPolicy(org_id=org_id)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    post = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not post or post.status != "published":
        raise ValueError("Target post not found or not published")

    if not settings.agents_enabled:
        return []

    if not force and random.random() > float(settings.spawn_probability_base):
        return []

    usage = _get_or_create_usage(db, org_id)
    if usage.actions_spawned >= int(settings.max_actions_per_day):
        return []

    agents = (
        db.query(AgentProfile)
        .filter(AgentProfile.org_id == org_id, AgentProfile.is_enabled == True)  # noqa: E712
        .order_by(AgentProfile.id.asc())
        .all()
    )
    if not agents:
        return []

    # cooldown: agent can't spawn again on same post within last 10 minutes
    cooldown_since = datetime.now(timezone.utc) - timedelta(minutes=10)
    recent_agent_ids = {
        r[0]
        for r in db.query(AgentAction.agent_id)
        .filter(
            AgentAction.org_id == org_id,
            AgentAction.target_type == "post",
            AgentAction.target_id == post.id,
            AgentAction.created_at >= cooldown_since,
        )
        .all()
    }

    available = [a for a in agents if a.id not in recent_agent_ids] or agents[:]

    n = min(int(max_n), int(settings.max_agents_per_post), len(available))
    if n <= 0:
        return []

    # replies: 30% chance if there are existing published comments
    published_comments = (
        db.query(Comment)
        .filter(Comment.org_id == org_id, Comment.post_id == post.id, Comment.status == "published")
        .order_by(desc(Comment.created_at))
        .limit(50)
        .all()
    )
    do_replies = bool(published_comments) and (random.random() < 0.30)

    chosen = random.sample(available, k=n)

    existing_hashes = {
        r[0]
        for r in db.query(AgentAction.prompt_hash)
        .filter(AgentAction.org_id == org_id, AgentAction.target_type.in_(["post", "comment"]))
        .all()
        if r[0]
    }

    created: list[AgentAction] = []

    for agent in chosen:
        persona = Persona(
            display_name=agent.display_name,
            style=agent.style or "concise",
            topics=agent.topics or "",
            persona_seed=agent.persona_seed or "",
        )

        content = write_comment(persona, post_title=post.title, post_body=post.body_md)

        # policy scoring
        policy_score = 0
        policy_reason = "persona_template"
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                res = score_text_with_deepseek(content)
                policy_score = int(res.score)
                policy_reason = res.reason or "deepseek"
            except Exception:
                  policy_score = 50
                  policy_reason = "deepseek_error"

        # decide status
        auto_ok = int(getattr(policy, "auto_approve_threshold", 20))
        auto_reject = int(getattr(policy, "auto_reject_threshold", 80))
        if policy_score <= auto_ok:
            status = "published"
        elif policy_score >= auto_reject:
            status = "rejected"
        else:
            status = "needs_review" if bool(getattr(policy, "require_human_review", True)) else "published"

        ph = _h(f"{org_id}:{post.id}:{agent.id}:{content}")
        if ph in existing_hashes:
            content = content + "(variant)"
            ph = _h(f"{org_id}:{post.id}:{agent.id}:{content}")

        target_type = "post"
        target_id = post.id
        action_type = "comment"
        if do_replies:
            parent = random.choice(published_comments)
            target_type = "comment"
            target_id = parent.id
            action_type = "reply"

        published_at = datetime.now(timezone.utc) if status == "published" else None

        # Build deterministic idempotency key
        idem = _idempotency_key(
            str(org_id),
            str(post.id),
            str(agent.id),
            target_type,
            str(target_id),
            action_type,
            content,
        )

        # If not forcing, skip if already exists
        if not force:
            existing = (
                db.query(AgentAction)
                .filter(AgentAction.org_id == org_id, AgentAction.idempotency_key == idem)
                .first()
            )
            if existing:
                created.append(existing)
                continue
        else:
            # force=true => allow a legit variant by salting idempotency
            # keep your "(variant)" marker if you want, but now it's real idempotency separation
            content = content + "(variant)"
            idem = _idempotency_key(idem, "force")

        aa = AgentAction(
            org_id=org_id,
            idempotency_key=idem,
            agent_id=agent.id,
            target_type=target_type,
            target_id=target_id,
            action_type=action_type,
            status=status,
            content=content,
            policy_score=policy_score,
            policy_reason=policy_reason,
            llm_provider="deepseek" if os.getenv("DEEPSEEK_API_KEY") else "",
            llm_model=os.getenv("DEEPSEEK_MODEL", "") if os.getenv("DEEPSEEK_API_KEY") else "",
            prompt_hash=ph,
            published_at=published_at,
        )
        try:
            db.add(aa)
            created.append(aa)
        except IntegrityError:
            db.rollback()
            existing = (
                db.query(AgentAction)
                .filter(
                    AgentAction.org_id == org_id,
                    AgentAction.idempotency_key == idem
                )
                .first()
            )
            if existing:
                created.append(existing)
                continue
            raise

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # In rare concurrent race, re-fetch all by idempotency keys
        created = (
            db.query(AgentAction)
            .filter(AgentAction.org_id == org_id)
            .order_by(AgentAction.id.desc())
            .limit(len(created))
            .all()
        )

    for x in created:
        db.refresh(x)

    usage.actions_spawned += len(created)
    usage.actions_published += sum(1 for x in created if x.status == "published")
    db.add(usage)
    db.commit()

    return created



def _materialize_published_comment_from_action(db, action) -> None:
    """
    MVP: If an agent action is published and represents a comment/reply,
    persist a Comment row so the public blog can render it.
    This function adapts to the current Comment schema (only sets existing columns).
    """
    try:
        # late import safety
        from sqlalchemy import inspect as sa_inspect
        comment_cols = {c.name for c in Comment.__table__.columns}
    except Exception:
        return

    # Only materialize published comment-like actions
    if getattr(action, "status", None) != "published":
        return
    if getattr(action, "action_type", None) not in ("comment", "reply"):
        return

    org_id = getattr(action, "org_id", None)
    agent_id = getattr(action, "agent_id", None)
    target_type = getattr(action, "target_type", None)
    target_id = getattr(action, "target_id", None)
    content = getattr(action, "content", None)

    # Determine post_id / parent_comment_id depending on target_type
    post_id = None
    parent_comment_id = None

    if target_type == "post":
        post_id = target_id
    elif target_type == "comment":
        parent_comment_id = target_id
        # try to resolve post_id from parent comment if possible
        try:
            parent = db.query(Comment).filter(Comment.id == parent_comment_id).one_or_none()
            if parent is not None and hasattr(parent, "post_id"):
                post_id = parent.post_id
        except Exception:
            pass
    else:
        return

    # Build kwargs only for existing columns
    data = {}
    for k, v in {
        "org_id": org_id,
        "post_id": post_id,
        "parent_comment_id": parent_comment_id,
        "agent_id": agent_id,
        "author_agent_id": agent_id,
        "author_type": "agent",
        "content": content,
        "body": content,
        "text": content,
        "status": "published",
        "published_at": getattr(action, "published_at", None),
        "created_at": getattr(action, "created_at", None),
    }.items():
        if k in comment_cols and v is not None:
            data[k] = v
        elif k in comment_cols and v is None and k in ("published_at", "created_at"):
            # allow nullable timestamps if schema expects them
            data[k] = None

    # Idempotency (best-effort without schema changes):
    # If schema has source_action_id, use it. Otherwise dedupe by core fields.
    if "source_action_id" in comment_cols:
        data["source_action_id"] = getattr(action, "id", None)
        exists = db.query(Comment).filter(Comment.source_action_id == data["source_action_id"]).one_or_none()
        if exists:
            return
    else:
        q = db.query(Comment)
        if "org_id" in comment_cols and org_id is not None:
            q = q.filter(Comment.org_id == org_id)
        if "post_id" in comment_cols and post_id is not None:
            q = q.filter(Comment.post_id == post_id)
        if "author_agent_id" in comment_cols and agent_id is not None:
            q = q.filter(Comment.author_agent_id == agent_id)
        if "agent_id" in comment_cols and agent_id is not None:
            q = q.filter(Comment.agent_id == agent_id)
        # content/body/text whichever exists
        if "content" in comment_cols and content is not None:
            q = q.filter(Comment.content == content)
        elif "body" in comment_cols and content is not None:
            q = q.filter(Comment.body == content)
        elif "text" in comment_cols and content is not None:
            q = q.filter(Comment.text == content)

        if q.first() is not None:
            return

    try:
        c = Comment(**data)
        db.add(c)
        db.commit()
    except Exception:
        db.rollback()
        return

