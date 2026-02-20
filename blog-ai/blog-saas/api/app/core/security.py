import os
from datetime import datetime, timedelta
from typing import Any, Optional
from jose import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.user import User
# =========================
# Password hashing (stable)
# =========================
# Use PBKDF2-SHA256 to avoid bcrypt backend issues and 72-byte limit.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        # Old/invalid hashes should NOT crash login; treat as invalid.
        return False


def verify_and_update_password(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
    """
    Verify password and optionally return a new hash if the stored hash should be upgraded.
    Returns: (ok, new_hash_or_none)
    """
    try:
        ok = pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False, None

    if not ok:
        return False, None

    # If passlib considers the hash deprecated/outdated, rehash.
    if pwd_context.needs_update(hashed_password):
        return True, pwd_context.hash(plain_password)

    return True, None


# =========================
# JWT
# =========================
def _jwt_secret_key() -> str:
    return os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret"

def _jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def _get_secret() -> str:
    return os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret"

def _get_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(
    subject: str,
    expires_minutes: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, _jwt_secret_key(), algorithm=_jwt_algorithm())



def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _jwt_secret_key(), algorithms=[_jwt_algorithm()])

bearer_scheme = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user