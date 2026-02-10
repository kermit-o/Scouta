from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import hash_password, verify_and_update_password, create_access_token
from app.models.user import User
from app.api.v1.schemas.auth import RegisterIn, LoginIn, TokenOut

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=token)


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
    return TokenOut(access_token=token)
