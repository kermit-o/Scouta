from typing import Generator, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import decode_token
from app.models.user import User
from app.models.org_member import OrgMember

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_org_role(
    org_id: int,
    allowed_roles: set[str],
    db: Session,
    user: User,
) -> OrgMember:
    m = (
        db.query(OrgMember)
        .filter(OrgMember.org_id == org_id, OrgMember.user_id == user.id)
        .one_or_none()
    )
    if not m:
        raise HTTPException(status_code=403, detail="Not a member of this org")
    if m.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient role")
    return m

def require_superuser(user: User = Depends(get_current_user)) -> User:
    if not getattr(user, "is_superuser", False):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Superuser access required")
    return user
