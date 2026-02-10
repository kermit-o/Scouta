from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.post import Post
from app.api.v1.schemas.posts import PostOut

router = APIRouter(tags=["admin"])

@router.get("/orgs/{org_id}/admin/posts", response_model=list[PostOut])
def admin_list_posts(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = Query(default="published"),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[PostOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    q = db.query(Post).filter(Post.org_id == org_id)
    if status:
        q = q.filter(Post.status == status)

    rows = q.order_by(desc(Post.published_at), desc(Post.created_at)).limit(limit).all()
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
