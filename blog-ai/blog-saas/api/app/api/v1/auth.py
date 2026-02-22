import os
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import hash_password, verify_and_update_password, create_access_token
from app.models.user import User
from app.api.v1.schemas.auth import RegisterIn, LoginIn, TokenOut
from app.services.email_service import send_verification_email

router = APIRouter(tags=["auth"])

@router.post("/auth/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")

    token = secrets.token_urlsafe(32)
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        username=payload.username,
        display_name=payload.display_name or payload.username,
        avatar_url="",
        bio="",
        is_verified=False,
        verification_token=token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_verification_email(payload.email, user.username, token)

    return {"message": "Registration successful. Please check your email to verify your account."}

@router.get("/auth/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.is_verified = True
    user.verification_token = None
    db.add(user)
    db.commit()
    access_token = create_access_token(subject=str(user.id))
    return TokenOut(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url or "",
    )

@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    ok, new_hash = verify_and_update_password(payload.password, user.password_hash)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
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
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url or "",
        "bio": user.bio or "",
        "created_at": str(user.created_at),
        "is_verified": user.is_verified,
    }


@router.post("/auth/forgot-password")
def forgot_password(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email", "")
    user = db.query(User).filter(User.email == email).one_or_none()
    # Siempre responder igual para no revelar si el email existe
    if user:
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        db.add(user)
        db.commit()
        from app.services.email_service import send_reset_email
        send_reset_email(email, user.username, token)
    return {"message": "If that email exists, you will receive a reset link."}


@router.post("/auth/reset-password")
def reset_password(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("token", "")
    new_password = payload.get("password", "")
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and password required")
    user = db.query(User).filter(User.verification_token == token).one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    from app.core.security import hash_password
    user.password_hash = hash_password(new_password)
    user.verification_token = None
    user.is_verified = True
    db.add(user)
    db.commit()
    access_token = create_access_token(subject=str(user.id))
    return TokenOut(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url or "",
    )


import httpx

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://scouta-production.up.railway.app/api/v1/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://serene-eagerness-production.up.railway.app")

@router.get("/auth/google")
def google_login():
    """Redirige a Google OAuth"""
    import urllib.parse
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@router.get("/auth/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """Callback de Google OAuth"""
    from fastapi.responses import RedirectResponse

    # Intercambiar code por token
    token_res = httpx.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    token_data = token_res.json()
    access_token_google = token_data.get("access_token")
    if not access_token_google:
        return RedirectResponse(f"{FRONTEND_URL}/login?error=google_failed")

    # Obtener info del usuario
    user_info = httpx.get("https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token_google}"}
    ).json()

    email = user_info.get("email")
    name = user_info.get("name", "")
    picture = user_info.get("picture", "")

    if not email:
        return RedirectResponse(f"{FRONTEND_URL}/login?error=no_email")

    # Buscar o crear usuario
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        import re
        base_username = re.sub(r"[^a-z0-9]", "", email.split("@")[0].lower())[:20] or "user"
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).one_or_none():
            username = f"{base_username}{counter}"
            counter += 1
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            username=username,
            display_name=name or username,
            avatar_url=picture,
            bio="",
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Actualizar avatar si cambió
        if picture and not user.avatar_url:
            user.avatar_url = picture
            db.add(user)
            db.commit()

    token = create_access_token(subject=str(user.id))

    # Redirigir al frontend con token
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback?token={token}&user_id={user.id}&username={user.username}&display_name={user.display_name or ''}&avatar_url={user.avatar_url or ''}"
    )


@router.put("/auth/profile")
def update_profile(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(__import__("app.core.deps", fromlist=["get_current_user"]).get_current_user),
):
    """Actualizar perfil del usuario"""
    allowed = ["display_name", "bio", "avatar_url", "interests", "website", "location", "username"]
    for field in allowed:
        if field in payload and payload[field] is not None:
            # Verificar username único
            if field == "username":
                existing = db.query(User).filter(
                    User.username == payload[field],
                    User.id != user.id
                ).one_or_none()
                if existing:
                    raise HTTPException(status_code=409, detail="Username already taken")
            setattr(user, field, payload[field])
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url or "",
        "bio": user.bio or "",
        "interests": getattr(user, "interests", "") or "",
        "website": getattr(user, "website", "") or "",
        "location": getattr(user, "location", "") or "",
    }


@router.post("/posts/human")
def create_human_post(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(__import__("app.core.deps", fromlist=["get_current_user"]).get_current_user),
):
    """Crear post como usuario humano"""
    from app.models.post import Post
    import re, time

    title = payload.get("title", "").strip()
    body_md = payload.get("body_md", "").strip()
    excerpt = payload.get("excerpt", "").strip()
    org_id = payload.get("org_id", 1)

    if not title or not body_md:
        raise HTTPException(status_code=400, detail="Title and body are required")

    # Generar slug
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80]
    slug = f"{slug}-{int(time.time())}"

    post = Post(
        org_id=org_id,
        author_user_id=user.id,
        author_agent_id=None,
        title=title,
        slug=slug,
        body_md=body_md,
        excerpt=excerpt or body_md[:200],
        status="published",
        source="human",
        debate_status="none",
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    # Extraer tags
    try:
        from app.services.tag_extractor import save_tags_for_post
        save_tags_for_post(db, post.id, post.title, post.body_md)
    except Exception:
        pass

    return {"id": post.id, "title": post.title, "slug": post.slug}
