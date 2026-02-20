from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.post import Post
from app.api.v1.schemas.posts import PostCreateIn, PostPatchIn, PostOut

router = APIRouter(tags=["posts"])

@router.get("/orgs/{org_id}/posts", response_model=list[PostOut])
def list_posts(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[PostOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)

    query = db.query(Post).filter(Post.org_id == org_id)
    if status:
        query = query.filter(Post.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter((Post.title.ilike(like)) | (Post.body_md.ilike(like)))

    rows = query.order_by(desc(Post.created_at)).limit(limit).all()
    return [
        PostOut(
            id=p.id,
            org_id=p.org_id,
            author_user_id=p.author_user_id,
            title=p.title,
            slug=p.slug,
            body_md=p.body_md,
            status=p.status,
            created_at=p.created_at.isoformat(),
            published_at=p.published_at.isoformat() if p.published_at else None,
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
        status=p.status,
        created_at=p.created_at.isoformat(),
        published_at=None,
    )

@router.get("/orgs/{org_id}/posts/{post_id}", response_model=PostOut)
def get_post(
    org_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PostOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)
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
        status=p.status,
        created_at=p.created_at.isoformat(),
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
        status=p.status,
        created_at=p.created_at.isoformat(),
        published_at=p.published_at.isoformat() if p.published_at else None,
    )
