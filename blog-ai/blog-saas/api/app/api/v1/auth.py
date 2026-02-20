from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import hash_password, verify_and_update_password, create_access_token
from app.models.user import User
from app.api.v1.schemas.auth import RegisterIn, LoginIn, TokenOut

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    # Verificar email único
    if db.query(User).filter(User.email == payload.email).one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Verificar username único
    if db.query(User).filter(User.username == payload.username).one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        username=payload.username,
        display_name=payload.display_name or payload.username,
        avatar_url="",
        bio="",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenOut(
        access_token=token,
        user_id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )


@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    ok, new_hash = verify_and_update_password(payload.password, user.password_hash)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if new_hash:
        user.password_hash = new_hash
        db.add(user)
        db.commit()

    token = create_access_token(subject=str(user.id))
    return TokenOut(
        access_token=token,
        user_id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url or "",
    )


@router.get("/auth/me")
def me(
    db: Session = Depends(get_db),
    user: User = Depends(__import__("app.core.deps", fromlist=["get_current_user"]).get_current_user),
):
    """Retorna perfil del usuario autenticado"""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url or "",
        "bio": user.bio or "",
        "created_at": str(user.created_at),
    }
