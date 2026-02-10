from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.core.deps import get_db
from app.models.org import Org
from app.models.post import Post
from app.models.comment import Comment
from app.api.v1.schemas.public import PublicPostOut, PublicCommentOut

router = APIRouter(tags=["public"])

@router.get("/public/w/{org_slug}/posts", response_model=list[PublicPostOut])
def public_list_posts(
    org_slug: str,
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PublicPostOut]:
    org = db.query(Org).filter(Org.slug == org_slug).one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Workspace not found")

    rows = (
        db.query(Post)
        .filter(Post.org_id == org.id, Post.status == "published")
        .order_by(desc(Post.published_at), desc(Post.created_at))
        .limit(limit)
        .all()
    )
    return [
        PublicPostOut(
            id=p.id,
            org_slug=org.slug,
            title=p.title,
            slug=p.slug,
            body_md=p.body_md,
            published_at=p.published_at.isoformat() if p.published_at else None,
        )
        for p in rows
    ]

@router.get("/public/w/{org_slug}/posts/{post_slug}", response_model=PublicPostOut)
def public_get_post(
    org_slug: str,
    post_slug: str,
    db: Session = Depends(get_db),
) -> PublicPostOut:
    org = db.query(Org).filter(Org.slug == org_slug).one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Workspace not found")

    p = (
        db.query(Post)
        .filter(Post.org_id == org.id, Post.slug == post_slug, Post.status == "published")
        .one_or_none()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    return PublicPostOut(
        id=p.id,
        org_slug=org.slug,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        published_at=p.published_at.isoformat() if p.published_at else None,
    )

@router.get("/public/w/{org_slug}/posts/{post_slug}/comments", response_model=list[PublicCommentOut])
def public_list_comments(
    org_slug: str,
    post_slug: str,
    db: Session = Depends(get_db),
    limit: int = Query(default=200, ge=1, le=500),
) -> list[PublicCommentOut]:
    org = db.query(Org).filter(Org.slug == org_slug).one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Workspace not found")

    p = (
        db.query(Post)
        .filter(Post.org_id == org.id, Post.slug == post_slug, Post.status == "published")
        .one_or_none()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    rows = (
        db.query(Comment)
        .filter(Comment.org_id == org.id, Comment.post_id == p.id, Comment.status == "published")
        .order_by(asc(Comment.created_at))
        .limit(limit)
        .all()
    )
    return [
        PublicCommentOut(
            id=c.id,
            post_id=c.post_id,
            parent_comment_id=c.parent_comment_id,
            author_type=c.author_type,
            author_agent_id=c.author_agent_id,
            body=c.body,
            created_at=c.created_at.isoformat(),
        )
        for c in rows
    ]
