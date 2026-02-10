import os
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

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
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret"
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def create_access_token(
    subject: str,
    expires_minutes: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
