import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import hash_password, verify_and_update_password, create_access_token
from app.models.user import User
from app.api.v1.schemas.auth import RegisterIn, LoginIn, TokenOut
from app.services.email_service import send_verification_email
from app.services.turnstile import verify_turnstile
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["auth"])

def _ensure_org_member(db, user_id: int, org_id: int = 1):
    """Ensures user has an org_member record. Creates one if missing."""
    from app.models.org_member import OrgMember
    existing = db.query(OrgMember).filter(
        OrgMember.user_id == user_id,
        OrgMember.org_id == org_id,
    ).first()
    if not existing:
        member = OrgMember(org_id=org_id, user_id=user_id, role="viewer")
        db.add(member)
        db.commit()

@router.post("/auth/register")
@limiter.limit("5/minute")
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)):
    if not verify_turnstile(payload.cf_turnstile_token or "", request.client.host if request.client else ""):
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed")
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
    _ensure_org_member(db, user.id)
    # Send welcome email
    try:
        from app.services.email_service import send_welcome_email, send_admin_notification
        send_welcome_email(user.email, user.username or user.display_name or 'friend')
        send_admin_notification("new_user", username=user.username or user.email, email=user.email)
    except Exception:
        pass

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
@limiter.limit("10/minute")
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    if not verify_turnstile(payload.cf_turnstile_token or "", request.client.host if request.client else ""):
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed")
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    ok, new_hash = verify_and_update_password(payload.password, user.password_hash)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
    if getattr(user, "is_banned", False):
        reason = getattr(user, "ban_reason", "") or "violation of community guidelines"
        raise HTTPException(status_code=403, detail=f"Account suspended: {reason}")
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
        "is_superuser": getattr(user, "is_superuser", False),
    }


@router.post("/auth/forgot-password")
@limiter.limit("3/minute")
def forgot_password(payload: dict, request: Request, db: Session = Depends(get_db)):
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
    _ensure_org_member(db, user.id)
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
def google_login(redirect_mobile: str = ""):
    """Redirige a Google OAuth"""
    import urllib.parse
    state = "mobile" if redirect_mobile == "1" else "web"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@router.get("/auth/google/callback")
def google_callback(code: str, state: str = "web", db: Session = Depends(get_db)):
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

    callback_params = f"token={token}&user_id={user.id}&username={user.username}&display_name={user.display_name or ''}&avatar_url={user.avatar_url or ''}"

    # Redirect to mobile app deep link or web frontend
    if state == "mobile":
        return RedirectResponse(f"scouta://auth/callback?{callback_params}")

    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?{callback_params}")


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

    media_url = payload.get("media_url") or None
    media_type = payload.get("media_type") or None
    if not title and not media_url:
        raise HTTPException(status_code=400, detail="Title is required")
    if not body_md and not media_url:
        raise HTTPException(status_code=400, detail="Body or media is required")

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
        media_url=media_url,
        media_type=media_type,
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
# redeploy Sat Mar 14 21:39:20 UTC 2026

@router.post("/admin/users/{user_id}/ban")
def ban_user(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(__import__("app.core.deps", fromlist=["get_current_user"]).get_current_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    action = payload.get("action", "ban")
    if action == "ban":
        user.is_banned = True
        user.ban_reason = payload.get("reason", "")
    elif action == "unban":
        user.is_banned = False
        user.ban_reason = None
    elif action == "flag":
        user.is_flagged = True
        user.flag_reason = payload.get("reason", "")
    elif action == "unflag":
        user.is_flagged = False
        user.flag_reason = None
    db.commit()
    return {"ok": True, "user_id": user_id, "action": action}
