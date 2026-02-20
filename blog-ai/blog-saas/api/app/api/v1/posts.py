from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.vote import Vote
from app.models.agent_profile import AgentProfile
from app.models.agent_profile import AgentProfile
from app.api.v1.schemas.posts import PostCreateIn, PostPatchIn, PostOut
from sqlalchemy import func

router = APIRouter(tags=["posts"])

@router.get("/orgs/{org_id}/posts", response_model=list[PostOut])
def list_posts(
    org_id: int,
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[PostOut]:
    query = db.query(Post).filter(Post.org_id == org_id)
    if status:
        query = query.filter(Post.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter((Post.title.ilike(like)) | (Post.body_md.ilike(like)))

    rows = query.order_by(desc(Post.created_at)).limit(limit).all()
    post_ids = [p.id for p in rows]

    # Agentes lookup
    agent_ids = {p.author_agent_id for p in rows if p.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    # Agentes lookup
    agent_ids = {p.author_agent_id for p in rows if p.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    # Comment counts
    comment_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids), Comment.status == "published")
        .group_by(Comment.post_id).all()
    ) if post_ids else {}

    # Upvote counts
    upvote_counts = dict(
        db.query(Comment.post_id, func.count(Vote.id))
        .join(Vote, Vote.comment_id == Comment.id)
        .filter(Comment.post_id.in_(post_ids), Vote.value == 1)
        .group_by(Comment.post_id).all()
    ) if post_ids else {}

    return [
        PostOut(
            id=p.id,
            org_id=p.org_id,
            author_user_id=p.author_user_id,
            title=p.title,
            slug=p.slug,
            body_md=p.body_md,
            excerpt=getattr(p, 'excerpt', None),
            status=p.status,
            debate_status=getattr(p, 'debate_status', None),
            source=getattr(p, 'source', None),
            created_at=p.created_at.isoformat() if p.created_at else "",
            published_at=p.published_at.isoformat() if p.published_at else None,
            comment_count=comment_counts.get(p.id, 0),
            upvote_count=upvote_counts.get(p.id, 0),
            author_agent_id=p.author_agent_id,
            author_agent_name=agents[p.author_agent_id].display_name if p.author_agent_id and p.author_agent_id in agents else None,
            author_type=getattr(p, 'author_type', 'agent'),
        )
        for p in rows
    ]

@router.post("/orgs/{org_id}/posts", response_model=PostOut)
def create_post(
    org_id: int,
    payload: PostCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PostOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    p = Post(
        org_id=org_id,
        author_user_id=user.id,
        title=payload.title,
        slug=payload.slug,
        body_md=payload.body_md or "",
        status="draft",
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    return PostOut(
        id=p.id,
        org_id=p.org_id,
        author_user_id=p.author_user_id,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        excerpt=getattr(p, "excerpt", None),
        status=p.status,
        debate_status=getattr(p, "debate_status", None),
        source=getattr(p, "source", None),
        created_at=p.created_at.isoformat() if p.created_at else "",
        published_at=None,
    )

@router.get("/orgs/{org_id}/posts/{post_id}", response_model=PostOut)
def get_post(
    org_id: int,
    post_id: int,
    db: Session = Depends(get_db),
) -> PostOut:
    p = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostOut(
        id=p.id,
        org_id=p.org_id,
        author_user_id=p.author_user_id,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        excerpt=getattr(p, "excerpt", None),
        status=p.status,
        debate_status=getattr(p, "debate_status", None),
        source=getattr(p, "source", None),
        created_at=p.created_at.isoformat() if p.created_at else "",
        published_at=p.published_at.isoformat() if p.published_at else None,
    )

@router.patch("/orgs/{org_id}/posts/{post_id}", response_model=PostOut)
def patch_post(
    org_id: int,
    post_id: int,
    payload: PostPatchIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PostOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    p = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        if data["status"] not in {"draft", "published"}:
            raise HTTPException(status_code=400, detail="Invalid status")
        if data["status"] == "published" and not p.published_at:
            p.published_at = datetime.now(timezone.utc)

    for k, v in data.items():
        setattr(p, k, v)

    db.add(p)
    db.commit()
    db.refresh(p)

    return PostOut(
        id=p.id,
        org_id=p.org_id,
        author_user_id=p.author_user_id,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        excerpt=getattr(p, "excerpt", None),
        status=p.status,
        debate_status=getattr(p, "debate_status", None),
        source=getattr(p, "source", None),
        created_at=p.created_at.isoformat() if p.created_at else "",
        published_at=p.published_at.isoformat() if p.published_at else None,
    )


@router.post("/orgs/{org_id}/posts/{post_id}/vote")
def vote_post(
    org_id: int,
    post_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from sqlalchemy import text
    value = payload.get("value", 1)
    if value not in (1, -1):
        raise HTTPException(status_code=400, detail="value must be 1 or -1")

    post = db.query(Post).filter(Post.id == post_id, Post.org_id == org_id).one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = db.execute(
        text("SELECT id, value FROM post_votes WHERE user_id=:uid AND post_id=:pid"),
        {"uid": user.id, "pid": post_id}
    ).first()

    if existing:
        if existing.value == value:
            db.execute(text("DELETE FROM post_votes WHERE user_id=:uid AND post_id=:pid"),
                      {"uid": user.id, "pid": post_id})
            action = "removed"
        else:
            db.execute(text("UPDATE post_votes SET value=:v WHERE user_id=:uid AND post_id=:pid"),
                      {"v": value, "uid": user.id, "pid": post_id})
            action = "changed"
    else:
        db.execute(text("INSERT INTO post_votes (user_id, post_id, value) VALUES (:uid, :pid, :v)"),
                  {"uid": user.id, "pid": post_id, "v": value})
        action = "added"
    db.commit()

    ups = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=1"), {"pid": post_id}).scalar()
    downs = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=-1"), {"pid": post_id}).scalar()
    return {"action": action, "upvotes": ups, "downvotes": downs}


@router.get("/orgs/{org_id}/posts/{post_id}/votes")
def get_post_votes(org_id: int, post_id: int, db: Session = Depends(get_db)) -> dict:
    from sqlalchemy import text
    ups = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=1"), {"pid": post_id}).scalar()
    downs = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=-1"), {"pid": post_id}).scalar()
    return {"upvotes": ups, "downvotes": downs}


@router.get("/orgs/{org_id}/feed")
def get_feed(
    org_id: int,
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list:
    from sqlalchemy import text
    import math
    from datetime import datetime, timezone

    rows = db.query(Post).filter(
        Post.org_id == org_id,
        Post.status == "published",
    ).order_by(desc(Post.created_at)).limit(100).all()

    post_ids = [p.id for p in rows]
    if not post_ids:
        return []

    # Comment counts
    comment_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids), Comment.status == "published")
        .group_by(Comment.post_id).all()
    )

    # Human comment counts (más valiosos)
    human_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids), Comment.status == "published", Comment.author_type == "user")
        .group_by(Comment.post_id).all()
    )

    # Upvote counts post
    placeholders = ",".join(str(i) for i in post_ids)
    upvote_counts = dict(
        db.execute(text(
            f"SELECT post_id, COUNT(*) as c FROM post_votes WHERE post_id IN ({placeholders}) AND value=1 GROUP BY post_id"
        )).fetchall()
    ) if post_ids else {}

    # Agentes
    agent_ids = {p.author_agent_id for p in rows if p.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    now = datetime.now(timezone.utc)

    def score(p):
        age_hours = max((now - p.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600, 0.1)
        ups = upvote_counts.get(p.id, 0)
        comments = comment_counts.get(p.id, 0)
        humans = human_counts.get(p.id, 0)
        raw = (ups * 3) + (humans * 5) + (comments * 1)
        return raw / math.pow(age_hours + 2, 1.5)

    scored = sorted(rows, key=score, reverse=True)[:limit]

    return [
        {
            "id": p.id,
            "org_id": p.org_id,
            "title": p.title,
            "slug": p.slug,
            "excerpt": getattr(p, "excerpt", None),
            "status": p.status,
            "debate_status": getattr(p, "debate_status", None),
            "created_at": p.created_at.isoformat() if p.created_at else "",
            "published_at": p.published_at.isoformat() if p.published_at else None,
            "author_type": getattr(p, "author_type", "agent"),
            "author_agent_id": p.author_agent_id,
            "author_agent_name": agents[p.author_agent_id].display_name if p.author_agent_id and p.author_agent_id in agents else None,
            "comment_count": comment_counts.get(p.id, 0),
            "upvote_count": upvote_counts.get(p.id, 0),
            "body_md": "",
        }
        for p in scored
    ]
