from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.comment import Comment
from app.models.post import Post
from app.api.v1.schemas.comments import CommentCreateIn, CommentOut

router = APIRouter(tags=["comments"])

@router.get("/orgs/{org_id}/posts/{post_id}/comments", response_model=list[CommentOut])
def list_comments(
    org_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(default=200, ge=1, le=500),
) -> list[CommentOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)

    exists = db.query(Post.id).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not exists:
        raise HTTPException(status_code=404, detail="Post not found")

    rows = (
        db.query(Comment)
        .filter(Comment.org_id == org_id, Comment.post_id == post_id, Comment.status == "published")
        .order_by(asc(Comment.created_at))
        .limit(limit)
        .all()
    )
    return [
        CommentOut(
            id=c.id,
            org_id=c.org_id,
            post_id=c.post_id,
            parent_comment_id=c.parent_comment_id,
            author_type=c.author_type,
            author_user_id=c.author_user_id,
            author_agent_id=c.author_agent_id,
            body=c.body,
            status=c.status,
            created_at=c.created_at.isoformat(),
        )
        for c in rows
    ]

@router.post("/orgs/{org_id}/posts/{post_id}/comments", response_model=CommentOut)
def create_comment(
    org_id: int,
    post_id: int,
    payload: CommentCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CommentOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)

    exists = db.query(Post.id).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not exists:
        raise HTTPException(status_code=404, detail="Post not found")

    c = Comment(
        org_id=org_id,
        post_id=post_id,
        parent_comment_id=payload.parent_comment_id,
        author_type="human",
        author_user_id=user.id,
        author_agent_id=None,
        body=payload.body,
        status="published",
    )
    db.add(c)
    db.commit()
    db.refresh(c)

    return CommentOut(
        id=c.id,
        org_id=c.org_id,
        post_id=c.post_id,
        parent_comment_id=c.parent_comment_id,
        author_type=c.author_type,
        author_user_id=c.author_user_id,
        author_agent_id=c.author_agent_id,
        body=c.body,
        status=c.status,
        created_at=c.created_at.isoformat(),
    )
