"""
Live streaming via LiveKit
"""
import os
import time
import random
import string
import json
import asyncio
import secrets

# AI agent live commenting throttles (env-configurable)
AI_LIVE_INITIAL_DELAY_SEC = int(os.getenv("AI_LIVE_INITIAL_DELAY_SEC", "60"))
AI_LIVE_INTERVAL_SEC = int(os.getenv("AI_LIVE_INTERVAL_SEC", "180"))
AI_LIVE_MAX_COMMENTS_PER_STREAM = int(os.getenv("AI_LIVE_MAX_COMMENTS_PER_STREAM", "20"))

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db, SessionLocal
from app.core.deps import get_current_user, require_superuser
from app.models.user import User
from app.core.logging import get_logger
from typing import Optional

router = APIRouter()
log = get_logger(__name__)

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")


def _gen_room_name() -> str:
    return "scouta-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def _make_identity(user_id: int) -> str:
    """Unique LiveKit identity per session — prevents collisions when the
    same user is connected from multiple devices."""
    return f"u{user_id}_{secrets.token_hex(3)}"


def _safe_int(value, default: int = 0) -> int:
    """Coerce a payload value to int without crashing on null / strings /
    bools. Used for client-supplied numeric fields where FastAPI hasn't
    validated the shape (we accept `dict` payloads here)."""
    try:
        if value is None or value is False:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _notify_followers_live(db: Session, host: User, room_name: str, title: str) -> None:
    """Insert an in-app 'live' notification for each of the host's followers.

    Best-effort: wrapped so a notification failure can't stop the host going
    live. Uses the existing notifications table columns; the room_name rides
    in post_title alongside the title so the bell can deep-link to the stream.
    """
    try:
        followers = db.execute(
            text("SELECT follower_id FROM follows WHERE following_id=:hid"),
            {"hid": host.id},
        ).fetchall()
        if not followers:
            return
        actor = host.display_name or host.username or f"user_{host.id}"
        for (follower_id,) in followers:
            db.execute(
                text(
                    "INSERT INTO notifications (user_id, type, actor_name, post_id, post_title) "
                    "VALUES (:uid, 'live', :actor, NULL, :title)"
                ),
                {"uid": follower_id, "actor": actor, "title": f"{room_name}|{title}"},
            )
        db.commit()
        log.info("live_followers_notified", host_id=host.id, count=len(followers))
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        log.warning("live_followers_notify_failed", host_id=host.id, error=str(e))


def _require_host(db: Session, room_name: str, user_id: int):
    """Raise 403 unless the caller is the original host of the live stream."""
    stream = db.execute(
        text("SELECT host_user_id FROM live_streams WHERE room_name=:room"),
        {"room": room_name},
    ).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    if stream.host_user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the host can do that")


def _create_livekit_token(room_name: str, identity: str, display_name: str = None, can_publish: bool = False) -> str:
    """Generate a LiveKit JWT token."""
    display = display_name or identity
    try:
        from livekit.api import AccessToken, VideoGrants
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(identity)
        token.with_name(display)
        token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=can_publish,
            can_subscribe=True,
            can_publish_data=True,
        ))
        return token.to_jwt()
    except Exception:
        import hmac, hashlib, base64 as b64
        header = b64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b'=').decode()
        payload = {
            "iss": LIVEKIT_API_KEY,
            "sub": identity,
            "name": display,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600 * 6,
            "video": {"room": room_name, "roomJoin": True, "canPublish": can_publish, "canSubscribe": True}
        }
        payload_b64 = b64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        sig_input = f"{header}.{payload_b64}"
        sig = hmac.new(LIVEKIT_API_SECRET.encode(), sig_input.encode(), hashlib.sha256).digest()
        sig_b64 = b64.urlsafe_b64encode(sig).rstrip(b'=').decode()
        return f"{sig_input}.{sig_b64}"


# ── WebSocket connections per room ────────────────────────────────────
_room_connections: dict[str, list[WebSocket]] = {}
# ── Blocked usernames per room ────────────────────────────────────────
# Write-through cache over the live_blocks table: hydrated from DB when a
# room's first socket connects, kept warm by the /block endpoint. The DB is
# the source of truth so blocks survive restarts; the cache keeps the
# per-message check in the WS hot loop fast.
_blocked_per_room: dict[str, set[str]] = {}


def _hydrate_blocks(room_name: str) -> None:
    """Load a room's blocked usernames from DB into the in-memory cache."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT username FROM live_blocks WHERE room_name=:room"),
            {"room": room_name},
        ).fetchall()
        _blocked_per_room[room_name] = {r[0] for r in rows}
    except Exception:
        _blocked_per_room.setdefault(room_name, set())
    finally:
        db.close()


def _ws_identity(websocket: WebSocket) -> Optional[dict]:
    """Authenticate a WS connection from its ?token= query param.

    Returns {id, username, display_name} for a valid token, else None
    (anonymous: may receive broadcasts but may not send chat). Identity is
    ALWAYS derived here from the signed token — never from client-supplied
    message fields — which is what prevents chat impersonation.
    """
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        return None
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name or user.username,
        }
    finally:
        db.close()


@router.post("/live/start")
def start_live(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Start a live stream — creates room and returns token."""
    title = payload.get("title", "Live Stream").strip()[:200]
    description = payload.get("description", "").strip()[:1000]
    if not title:
        raise HTTPException(status_code=400, detail="Title required")
    if len(title) < 3:
        raise HTTPException(status_code=400, detail="Title too short (min 3 chars)")

    # Terminar cualquier live anterior del mismo usuario
    db.execute(text(
        "UPDATE live_streams SET status='ended', ended_at=NOW() WHERE host_user_id=:uid AND status='live'"
    ), {"uid": user.id})
    db.commit()

    room_name = _gen_room_name()

    # Private room settings — payload values are user-supplied so coerce safely.
    is_private = bool(payload.get("is_private", False))
    access_type = payload.get("access_type", "public")
    entry_coin_cost = _safe_int(payload.get("entry_coin_cost"), 0)
    max_viewer_limit = _safe_int(payload.get("max_viewer_limit"), 0)
    password = payload.get("password", "") or ""

    password_hash = None
    if is_private and access_type == "password" and password:
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    db.execute(text(
        "INSERT INTO live_streams (room_name, title, host_user_id, org_id, description, status, "
        "is_private, password_hash, access_type, entry_coin_cost, max_viewer_limit) "
        "VALUES (:room, :title, :uid, 1, :desc, 'live', "
        ":is_private, :pw_hash, :access_type, :entry_cost, :max_limit)"
    ), {
        "room": room_name, "title": title, "uid": user.id, "desc": description,
        "is_private": is_private, "pw_hash": password_hash,
        "access_type": access_type if is_private else "public",
        "entry_cost": entry_coin_cost if is_private else 0, "max_limit": max_viewer_limit,
    })
    db.commit()

    from app.services.analytics import track_event
    track_event(
        db, "live_started",
        user_id=user.id, room=room_name, access_type=access_type if is_private else "public",
        is_private=is_private, entry_coin_cost=entry_coin_cost if is_private else 0,
    )

    # Notify followers that the host went live. Best-effort — must never break
    # going live. Public streams only (don't leak private streams to non-members).
    if not is_private:
        _notify_followers_live(db, user, room_name, title)

    token = _create_livekit_token(
        room_name,
        _make_identity(user.id),
        user.display_name or user.username or f"user_{user.id}",
        can_publish=True,
    )

    return {
        "room_name": room_name,
        "token": token,
        "livekit_url": LIVEKIT_URL,
        "title": title,
        "is_private": is_private,
    }


@router.post("/live/{room_name}/join")
def join_live(
    room_name: str,
    payload: dict = {},
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Join a live stream as viewer."""
    stream = db.execute(
        text("SELECT id, title, status, is_private, access_type, password_hash, entry_coin_cost, max_viewer_limit, viewer_count, host_user_id "
             "FROM live_streams WHERE room_name=:room"),
        {"room": room_name}
    ).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    if stream.status != "live":
        raise HTTPException(status_code=400, detail="Stream has ended")

    # Block host from joining their own stream as viewer (LiveKit identity collision)
    if stream.host_user_id == user.id:
        raise HTTPException(status_code=409, detail="already_broadcasting")

    # Private room access checks (host case already returned above)
    if stream.is_private:
        from app.models.room_access import RoomAccess

        # Check max viewer limit
        if stream.max_viewer_limit and stream.max_viewer_limit > 0 and stream.viewer_count >= stream.max_viewer_limit:
            raise HTTPException(status_code=403, detail="room_full")

        # Check if user already has access
        has_access = db.query(RoomAccess).filter(
            RoomAccess.room_name == room_name,
            RoomAccess.user_id == user.id,
        ).first()

        if not has_access:
            if stream.access_type == "password":
                password = payload.get("password", "")
                if not password:
                    raise HTTPException(status_code=403, detail="password_required")
                import hashlib
                if hashlib.sha256(password.encode()).hexdigest() != stream.password_hash:
                    raise HTTPException(status_code=403, detail="wrong_password")
                db.add(RoomAccess(room_name=room_name, user_id=user.id, access_type="password_entered"))
                db.commit()

            elif stream.access_type == "invite_only":
                raise HTTPException(status_code=403, detail="invite_only")

            elif stream.access_type == "paid":
                cost = stream.entry_coin_cost or 0
                if cost > 0:
                    from app.models.coin_wallet import CoinWallet
                    from app.models.coin_transaction import CoinTransaction
                    wallet = db.query(CoinWallet).filter(CoinWallet.user_id == user.id).first()
                    if not wallet or wallet.balance < cost:
                        raise HTTPException(status_code=402, detail=f"paid_entry:{cost}")
                    wallet.balance -= cost
                    wallet.lifetime_spent += cost
                    host_wallet = db.query(CoinWallet).filter(CoinWallet.user_id == stream.host_user_id).first()
                    if not host_wallet:
                        host_wallet = CoinWallet(user_id=stream.host_user_id, balance=0)
                        db.add(host_wallet)
                        db.flush()
                    host_wallet.balance += cost
                    host_wallet.lifetime_earned += cost
                    db.add(CoinTransaction(user_id=user.id, amount=-cost, type="room_entry", reference_id=room_name, description=f"Paid entry to {stream.title}"))
                    db.add(CoinTransaction(user_id=stream.host_user_id, amount=cost, type="gift_received", reference_id=room_name, description=f"Room entry fee from {user.display_name or user.username}"))
                db.add(RoomAccess(room_name=room_name, user_id=user.id, access_type="paid"))
                db.commit()

            elif stream.access_type == "followers":
                is_follower = db.execute(
                    text("SELECT id FROM follows WHERE follower_id=:fid AND following_id=:tid"),
                    {"fid": user.id, "tid": stream.host_user_id}
                ).first()
                if not is_follower:
                    raise HTTPException(status_code=403, detail="followers_only")
                db.add(RoomAccess(room_name=room_name, user_id=user.id, access_type="follower"))
                db.commit()

            elif stream.access_type == "subscribers":
                from app.models.user_subscription import UserSubscription
                is_sub = db.query(UserSubscription).filter(
                    UserSubscription.subscriber_id == user.id,
                    UserSubscription.creator_id == stream.host_user_id,
                    UserSubscription.status == "active",
                ).first()
                if not is_sub:
                    raise HTTPException(status_code=403, detail="subscribers_only")
                db.add(RoomAccess(room_name=room_name, user_id=user.id, access_type="subscriber"))
                db.commit()

            elif stream.access_type == "vip":
                from app.models.vip_list import VipList
                is_vip = db.query(VipList).filter(
                    VipList.owner_user_id == stream.host_user_id,
                    VipList.vip_user_id == user.id,
                ).first()
                if not is_vip:
                    raise HTTPException(status_code=403, detail="vip_only")
                db.add(RoomAccess(room_name=room_name, user_id=user.id, access_type="vip"))
                db.commit()

    token = _create_livekit_token(
        room_name,
        _make_identity(user.id),
        user.display_name or user.username or f"user_{user.id}",
        can_publish=False,
    )

    db.execute(text("UPDATE live_streams SET viewer_count = viewer_count + 1 WHERE room_name=:room"), {"room": room_name})
    db.commit()

    from app.services.analytics import track_event
    track_event(
        db, "live_joined",
        user_id=user.id, room=room_name,
        access_type=stream.access_type if stream.is_private else "public",
    )

    return {"token": token, "livekit_url": LIVEKIT_URL, "title": stream.title}


@router.post("/live/{room_name}/invite")
def invite_to_live(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Invite another user to publish (duo/group live)."""
    # Verify caller is the host
    stream = db.execute(
        text("SELECT host_user_id FROM live_streams WHERE room_name=:room AND status='live'"),
        {"room": room_name}
    ).first()
    if not stream or stream.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the host can invite users")

    invitee_username = payload.get("username")
    invitee = db.query(User).filter(User.username == invitee_username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")

    from app.models.room_access import RoomAccess
    existing = db.query(RoomAccess).filter(RoomAccess.room_name == room_name, RoomAccess.user_id == invitee.id).first()
    if not existing:
        db.add(RoomAccess(room_name=room_name, user_id=invitee.id, access_type="invited"))
        db.commit()

    token = _create_livekit_token(
        room_name,
        _make_identity(invitee.id),
        invitee.display_name or invitee.username,
        can_publish=True,
    )
    return {"token": token, "livekit_url": LIVEKIT_URL, "invited_user": invitee_username}


@router.post("/live/{room_name}/grant-access")
def grant_access(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host grants viewer access to a user for a private room."""
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username required")

    stream = db.execute(
        text("SELECT host_user_id FROM live_streams WHERE room_name=:room AND status='live'"),
        {"room": room_name}
    ).first()
    if not stream or stream.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Only host can grant access")

    invitee = db.query(User).filter(User.username == username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")

    from app.models.room_access import RoomAccess
    existing = db.query(RoomAccess).filter(RoomAccess.room_name == room_name, RoomAccess.user_id == invitee.id).first()
    if not existing:
        db.add(RoomAccess(room_name=room_name, user_id=invitee.id, access_type="invited"))
        db.commit()

    return {"ok": True, "granted_to": username}


@router.post("/live/{room_name}/end")
async def end_live(
    room_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """End a live stream — host only."""
    _require_host(db, room_name, user.id)
    db.execute(text(
        "UPDATE live_streams SET status='ended', ended_at=NOW() WHERE room_name=:room"
    ), {"room": room_name})
    db.commit()
    if room_name in _room_connections:
        ended_msg = json.dumps({"type": "stream_ended", "message": "Stream has ended"})
        async def _broadcast_ended():
            for ws in list(_room_connections.get(room_name, [])):
                try:
                    await ws.send_text(ended_msg)
                except Exception:
                    pass
            if room_name in _room_connections:
                del _room_connections[room_name]
        try:
            asyncio.ensure_future(_broadcast_ended())
        except Exception:
            del _room_connections[room_name]
    return {"ok": True}


@router.post("/admin/live/{room_name}/end")
async def admin_force_end_live(
    room_name: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_superuser),
):
    """Force-end a live stream regardless of who the host is. Emergency button
    for stuck/orphaned streams. Also tears down the LiveKit room."""
    from app.services.live_reconcile import force_end_stream
    ended = await force_end_stream(db, room_name)
    if not ended:
        raise HTTPException(status_code=404, detail="No live stream with that room")
    from app.services.analytics import track_event
    track_event(db, "live_force_ended", user_id=admin.id, room=room_name, alert=False)
    if room_name in _room_connections:
        ended_msg = json.dumps({"type": "stream_ended", "message": "Stream has ended"})
        for ws in list(_room_connections.get(room_name, [])):
            try:
                await ws.send_text(ended_msg)
            except Exception:
                pass
        _room_connections.pop(room_name, None)
    return {"ok": True, "room_name": room_name}


@router.post("/admin/live/reconcile")
async def admin_reconcile_lives(
    db: Session = Depends(get_db),
    admin: User = Depends(require_superuser),
):
    """Manually trigger LiveKit reconciliation — ends DB streams that LiveKit
    no longer has an active broadcast for. Runs automatically every few
    minutes too, but this lets an admin force a sweep on demand."""
    from app.services.live_reconcile import reconcile_live_streams
    result = await reconcile_live_streams(db)
    return result


@router.get("/live/{room_name}/join-anon")
def join_live_anon(room_name: str, db: Session = Depends(get_db)):
    """Join a live stream as anonymous viewer."""
    stream = db.execute(
        text("SELECT id, title, status, is_private FROM live_streams WHERE room_name=:room"),
        {"room": room_name}
    ).first()
    if not stream or stream.status != "live":
        raise HTTPException(status_code=404, detail="Stream not found or ended")
    if stream.is_private:
        raise HTTPException(status_code=403, detail="Private room — sign in to join")

    anon_name = "viewer_" + "".join(random.choices(string.ascii_lowercase, k=6))
    token = _create_livekit_token(room_name, anon_name, anon_name, can_publish=False)
    db.execute(text("UPDATE live_streams SET viewer_count = viewer_count + 1 WHERE room_name=:room"), {"room": room_name})
    db.commit()
    return {"token": token, "livekit_url": LIVEKIT_URL, "title": stream.title}


@router.post("/live/{room_name}/block")
async def block_from_live(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host blocks a user from the live chat. Mutes them via WS broadcast and
    drops their messages in the chat WS handler (see _is_blocked check)."""
    _require_host(db, room_name, user.id)
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    # Durable: persist the block so it survives restarts, then warm the cache.
    db.execute(
        text(
            "INSERT INTO live_blocks (room_name, username) VALUES (:room, :uname) "
            "ON CONFLICT (room_name, username) DO NOTHING"
        ),
        {"room": room_name, "uname": username},
    )
    db.commit()
    _blocked_per_room.setdefault(room_name, set()).add(username)
    await _broadcast(room_name, {"type": "blocked", "username": username})
    return {"ok": True, "blocked": username}


@router.post("/live/{room_name}/request-join")
async def request_join(
    room_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Viewer requests to join as co-host."""
    stream = db.execute(
        text("SELECT id, title FROM live_streams WHERE room_name=:room AND status='live'"),
        {"room": room_name}
    ).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    db.execute(
        text(
            "INSERT INTO live_join_requests (room_name, user_id, username, display_name) "
            "VALUES (:room, :uid, :uname, :dname) "
            "ON CONFLICT (room_name, user_id) DO UPDATE SET created_at = CURRENT_TIMESTAMP"
        ),
        {"room": room_name, "uid": user.id, "uname": user.username,
         "dname": user.display_name or user.username},
    )
    db.commit()

    await _broadcast(room_name, {
        "type": "join_request",
        "username": user.username,
        "display_name": user.display_name or user.username,
        "user_id": user.id,
        "room_name": room_name,
    })
    return {"ok": True, "message": "Request sent to host"}


@router.post("/live/{room_name}/accept-join")
async def accept_join(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host accepts a join request — returns publisher token for the requester."""
    _require_host(db, room_name, user.id)
    username = payload.get("username")
    accept = payload.get("accept", True)

    if not accept:
        db.execute(
            text("DELETE FROM live_join_requests WHERE room_name=:room AND username=:uname"),
            {"room": room_name, "uname": username},
        )
        db.commit()
        await _broadcast(room_name, {"type": "join_rejected", "username": username})
        return {"ok": True, "accepted": False}

    invitee = db.query(User).filter(User.username == username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")

    token = _create_livekit_token(
        room_name,
        _make_identity(invitee.id),
        invitee.display_name or invitee.username,
        can_publish=True,
    )

    db.execute(
        text("DELETE FROM live_join_requests WHERE room_name=:room AND username=:uname"),
        {"room": room_name, "uname": username},
    )
    db.commit()
    await _broadcast(room_name, {
        "type": "join_accepted",
        "username": username,
        "token": token,
        "livekit_url": LIVEKIT_URL,
        "room_name": room_name,
    })
    return {"ok": True, "accepted": True, "token": token, "livekit_url": LIVEKIT_URL}


@router.post("/live/{room_name}/kick")
async def kick_from_live(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host kicks a co-host from the live."""
    _require_host(db, room_name, user.id)
    username = payload.get("username")
    kick_msg = json.dumps({"type": "kicked", "username": username})
    for ws in list(_room_connections.get(room_name, [])):
        try:
            await ws.send_text(kick_msg)
        except Exception:
            pass
    return {"ok": True, "kicked": username}


@router.post("/live/{room_name}/leave")
async def leave_live(
    room_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Co-host leaves the live (back to viewer)."""
    leave_msg = json.dumps({
        "type": "cohost_left",
        "username": user.username,
        "display_name": user.display_name or user.username,
    })
    for ws in list(_room_connections.get(room_name, [])):
        try:
            await ws.send_text(leave_msg)
        except Exception:
            pass
    db.execute(text("UPDATE live_streams SET viewer_count = GREATEST(viewer_count - 1, 0) WHERE room_name=:room"), {"room": room_name})
    db.commit()
    return {"ok": True}


@router.get("/live/{room_name}/join-requests")
def get_join_requests(
    room_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Host polls for pending join requests."""
    _require_host(db, room_name, user.id)
    rows = db.execute(
        text(
            "SELECT user_id, username, display_name FROM live_join_requests "
            "WHERE room_name=:room ORDER BY created_at ASC"
        ),
        {"room": room_name},
    ).fetchall()
    return {"requests": [
        {"user_id": r[0], "username": r[1], "display_name": r[2]} for r in rows
    ]}


# ── Thumbnail capture ────────────────────────────────────────────────────────

@router.post("/live/{room_name}/thumbnail")
async def upload_thumbnail(
    room_name: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload a thumbnail JPEG for a live stream — host only.

    The host's frontend captures a frame from its local <video> every ~30s
    and POSTs the raw JPEG bytes here. We overwrite a single key per room
    in R2 and store a cache-busted URL so the /live list refreshes without
    serving stale browser cache hits.
    """
    _require_host(db, room_name, user.id)

    body = await request.body()
    if not body or len(body) < 200:
        raise HTTPException(status_code=400, detail="Empty thumbnail")
    if len(body) > 200 * 1024:  # 200KB max — JPEG quality 0.7 at 320×180 is well under this
        raise HTTPException(status_code=400, detail="Thumbnail too large (max 200KB)")

    from app.api.v1.upload import get_s3, R2_BUCKET, R2_PUBLIC_URL
    if not R2_PUBLIC_URL:
        raise HTTPException(status_code=503, detail="R2 not configured (R2_PUBLIC_URL missing)")

    key = f"thumbnails/live_{room_name}.jpg"
    try:
        s3 = get_s3()
        s3.put_object(
            Bucket=R2_BUCKET,
            Key=key,
            Body=body,
            ContentType="image/jpeg",
            CacheControl="public, max-age=30",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"R2 error: {e}")

    public_url = f"{R2_PUBLIC_URL}/{key}?t={int(time.time())}"
    db.execute(
        text("UPDATE live_streams SET thumbnail_url=:url WHERE room_name=:room"),
        {"url": public_url, "room": room_name},
    )
    db.commit()
    return {"ok": True, "thumbnail_url": public_url}


# ── Reactions (ephemeral floating hearts) ────────────────────────────────────

# Allowlisted reaction emojis. Restricting the set keeps the WS payload safe
# to render in the DOM (no arbitrary client-supplied strings) and keeps the
# UI coherent. ❤️ is the default.
_REACTION_EMOJIS = {"❤️", "😂", "😮", "😢", "👏", "🔥", "🎉", "💯"}


@router.post("/live/{room_name}/react")
async def send_reaction(
    room_name: str,
    payload: dict,
    user: User = Depends(get_current_user),
):
    """Broadcast a floating reaction to everyone in the room.

    Ephemeral by design — reactions are high-frequency and disposable, so we
    don't persist them; we just fan them out over the WS for the float
    animation. Identity comes from the authenticated user, never the payload.
    """
    emoji = payload.get("emoji", "❤️")
    if emoji not in _REACTION_EMOJIS:
        emoji = "❤️"
    await _broadcast(room_name, {
        "type": "reaction",
        "emoji": emoji,
        "username": user.username,
    })
    return {"ok": True}


# ── Gift system ──────────────────────────────────────────────────────────────

@router.get("/live/gifts/catalog")
def get_gift_catalog(db: Session = Depends(get_db)):
    """Return available gifts."""
    from app.models.gift import GiftCatalog
    gifts = db.query(GiftCatalog).order_by(GiftCatalog.sort_order).all()
    return {"gifts": [
        {"id": g.id, "name": g.name, "emoji": g.emoji, "coin_cost": g.coin_cost, "animation_type": g.animation_type}
        for g in gifts
    ]}


@router.post("/live/{room_name}/gift")
async def send_gift(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a gift during a live stream."""
    from app.models.gift import GiftCatalog, GiftSend
    from app.models.coin_wallet import CoinWallet
    from app.models.coin_transaction import CoinTransaction

    gift_id = payload.get("gift_id")
    if not gift_id:
        raise HTTPException(status_code=400, detail="gift_id required")

    gift = db.query(GiftCatalog).filter(GiftCatalog.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    stream = db.execute(
        text("SELECT id, host_user_id, status FROM live_streams WHERE room_name=:room"),
        {"room": room_name}
    ).first()
    if not stream or stream.status != "live":
        raise HTTPException(status_code=404, detail="Stream not found or ended")
    if stream.host_user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot gift yourself")

    host_user_id = stream.host_user_id

    sender_wallet = db.query(CoinWallet).filter(CoinWallet.user_id == user.id).with_for_update().first()
    if not sender_wallet or sender_wallet.balance < gift.coin_cost:
        raise HTTPException(status_code=402, detail="Insufficient coins")

    host_wallet = db.query(CoinWallet).filter(CoinWallet.user_id == host_user_id).with_for_update().first()
    if not host_wallet:
        host_wallet = CoinWallet(user_id=host_user_id, balance=0)
        db.add(host_wallet)
        db.flush()

    PLATFORM_FEE = 0.20
    fee_amount = max(1, int(gift.coin_cost * PLATFORM_FEE)) if gift.coin_cost >= 5 else 0
    host_amount = gift.coin_cost - fee_amount

    sender_wallet.balance -= gift.coin_cost
    sender_wallet.lifetime_spent += gift.coin_cost
    host_wallet.withdrawable_balance += host_amount
    host_wallet.lifetime_earned += host_amount

    gift_send = GiftSend(
        stream_room_name=room_name,
        sender_user_id=user.id,
        recipient_user_id=host_user_id,
        gift_id=gift.id,
        coin_amount=gift.coin_cost,
    )
    db.add(gift_send)
    db.flush()

    from app.models.platform_earnings import PlatformEarnings
    db.add(PlatformEarnings(
        stream_room_name=room_name,
        gift_send_id=gift_send.id,
        amount=gift.coin_cost,
        fee_amount=fee_amount,
        host_amount=host_amount,
    ))

    db.add(CoinTransaction(
        user_id=user.id,
        amount=-gift.coin_cost,
        type="gift_sent",
        reference_id=f"gift_{room_name}_{gift.id}",
        description=f"Sent {gift.name} to host",
    ))
    db.add(CoinTransaction(
        user_id=host_user_id,
        amount=host_amount,
        type="gift_received",
        reference_id=f"gift_{room_name}_{gift.id}",
        description=f"Received {gift.name} from {user.display_name or user.username} ({host_amount} coins after 20% fee)",
    ))
    db.commit()

    from app.services.analytics import track_event
    track_event(
        db, "gift_sent",
        user_id=user.id, recipient_user_id=host_user_id, room=room_name,
        gift_id=gift.id, coins=gift.coin_cost, host_amount=host_amount,
    )

    sender_name = user.display_name or user.username or f"user_{user.id}"
    gift_msg = json.dumps({
        "type": "gift",
        "sender": sender_name,
        "sender_username": user.username,
        "gift_name": gift.name,
        "emoji": gift.emoji,
        "coin_amount": gift.coin_cost,
        "animation": gift.animation_type,
    })
    for ws in list(_room_connections.get(room_name, [])):
        try:
            await ws.send_text(gift_msg)
        except Exception:
            pass

    return {
        "ok": True,
        "new_balance": sender_wallet.balance,
        "gift": {"name": gift.name, "emoji": gift.emoji, "coin_cost": gift.coin_cost},
    }


@router.get("/live/{room_name}/top-gifters")
def get_top_gifters(room_name: str, db: Session = Depends(get_db)):
    """Leaderboard: top 10 gifters for a stream."""
    rows = db.execute(text(
        "SELECT gs.sender_user_id, u.username, u.display_name, u.avatar_url, "
        "SUM(gs.coin_amount) as total_coins, COUNT(*) as gift_count "
        "FROM gift_sends gs JOIN users u ON gs.sender_user_id = u.id "
        "WHERE gs.stream_room_name = :room "
        "GROUP BY gs.sender_user_id, u.username, u.display_name, u.avatar_url "
        "ORDER BY total_coins DESC LIMIT 10"
    ), {"room": room_name}).fetchall()
    return {"gifters": [
        {
            "user_id": r[0], "username": r[1], "display_name": r[2], "avatar_url": r[3],
            "total_coins": r[4], "gift_count": r[5],
        }
        for r in rows
    ]}


@router.get("/live/active")
def list_active_streams(db: Session = Depends(get_db)):
    """List all active live streams (public + private with badge)."""
    rows = db.execute(text(
        "SELECT ls.room_name, ls.title, ls.viewer_count, ls.started_at, ls.description, "
        "u.username, u.display_name, ls.is_private, ls.access_type, ls.entry_coin_cost, "
        "ls.thumbnail_url "
        "FROM live_streams ls JOIN users u ON ls.host_user_id = u.id "
        "WHERE ls.status = 'live' ORDER BY ls.viewer_count DESC LIMIT 20"
    )).fetchall()
    return {"streams": [
        {
            "room_name": r[0], "title": r[1] if not r[7] else "Private Stream",
            "viewer_count": r[2],
            "started_at": r[3].isoformat() if r[3] else None,
            "description": r[4] if not r[7] else "",
            "host_username": r[5], "host_display_name": r[6],
            "is_private": bool(r[7]),
            "access_type": r[8] or "public",
            "entry_coin_cost": r[9] or 0,
            # Hide thumbnail of private streams from anonymous /live feed —
            # otherwise paid/invite-only previews leak to people who haven't paid.
            "thumbnail_url": r[10] if not r[7] else None,
        }
        for r in rows
    ]}


@router.get("/live/{room_name}/chat")
def get_chat_history(room_name: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get chat history for a room."""
    rows = db.execute(text(
        "SELECT username, display_name, message, is_agent, agent_name, created_at "
        "FROM live_chat WHERE room_name=:room ORDER BY created_at DESC LIMIT :limit"
    ), {"room": room_name, "limit": limit}).fetchall()
    return {"messages": [
        {"username": r[0], "display_name": r[1], "message": r[2],
         "is_agent": r[3], "agent_name": r[4], "created_at": r[5].isoformat() if r[5] else None}
        for r in reversed(rows)
    ]}


# ── WebSocket chat ────────────────────────────────────────────────────
async def _broadcast(room_name: str, payload: dict) -> None:
    """Send a JSON payload to every socket in a room, pruning dead ones."""
    data = json.dumps(payload)
    dead = []
    for ws in _room_connections.get(room_name, []):
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        try:
            _room_connections.get(room_name, []).remove(ws)
        except ValueError:
            pass


@router.websocket("/live/{room_name}/ws")
async def live_chat_ws(websocket: WebSocket, room_name: str):
    await websocket.accept()
    # Identity is derived from the token, NOT from message payloads. Anonymous
    # connections (no/invalid token) can receive broadcasts but cannot send.
    identity = _ws_identity(websocket)

    if room_name not in _room_connections:
        _room_connections[room_name] = []
    _room_connections[room_name].append(websocket)

    if len(_room_connections[room_name]) == 1:
        _hydrate_blocks(room_name)
        asyncio.create_task(_ai_agent_loop(room_name))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except (ValueError, TypeError):
                continue

            if msg.get("type", "chat") != "chat":
                continue  # reactions etc. handled via their own HTTP endpoints

            # Anonymous viewers may watch but not chat.
            if identity is None:
                try:
                    await websocket.send_text(json.dumps({"type": "error", "error": "auth_required"}))
                except Exception:
                    pass
                continue

            username = identity["username"]
            display_name = identity["display_name"]
            if username in _blocked_per_room.get(room_name, set()):
                continue

            message = str(msg.get("message", "")).strip()[:500]
            if not message:
                continue

            db = SessionLocal()
            try:
                db.execute(text(
                    "INSERT INTO live_chat (room_name, user_id, username, display_name, message) "
                    "VALUES (:room, :uid, :uname, :dname, :msg)"
                ), {"room": room_name, "uid": identity["id"], "uname": username,
                    "dname": display_name, "msg": message})
                db.commit()
            finally:
                db.close()

            await _broadcast(room_name, {
                "type": "chat",
                "username": username,
                "display_name": display_name,
                "message": message,
                "is_agent": False,
            })

    except WebSocketDisconnect:
        if websocket in _room_connections.get(room_name, []):
            _room_connections[room_name].remove(websocket)


async def _ai_agent_loop(room_name: str):
    """AI agents comment periodically on the live stream (throttled)."""
    await asyncio.sleep(AI_LIVE_INITIAL_DELAY_SEC)
    db = SessionLocal()
    try:
        stream = db.execute(
            text("SELECT title FROM live_streams WHERE room_name=:room AND status='live'"),
            {"room": room_name}
        ).first()
        if not stream:
            return
        title = stream[0]

        from app.services.llm_client import LLMClient
        from app.models.agent_profile import AgentProfile
        llm = LLMClient()
        agents = db.query(AgentProfile).filter(
            AgentProfile.org_id == 1,
            AgentProfile.is_enabled == True,
        ).order_by(AgentProfile.reputation_score.desc()).limit(20).all()

    finally:
        db.close()

    cycle = 0
    while _room_connections.get(room_name):
        await asyncio.sleep(AI_LIVE_INTERVAL_SEC)
        if not _room_connections.get(room_name):
            break
        if cycle >= AI_LIVE_MAX_COMMENTS_PER_STREAM:
            break

        db = SessionLocal()
        try:
            still_live = db.execute(
                text("SELECT status FROM live_streams WHERE room_name=:room"),
                {"room": room_name}
            ).first()
            if not still_live or still_live[0] != "live":
                break

            if not agents:
                continue
            agent = random.choice(agents)
            try:
                comment = llm.chat(
                    system=f"You are {agent.display_name}, {agent.bio or 'an AI debater'}. Keep responses under 20 words.",
                    user=f"React briefly to this live stream: '{title}'"
                )
                comment = comment.strip()[:200]
            except Exception:
                continue

            db.execute(text(
                "INSERT INTO live_chat (room_name, message, is_agent, agent_name) "
                "VALUES (:room, :msg, TRUE, :aname)"
            ), {"room": room_name, "msg": comment, "aname": agent.display_name})
            db.commit()

            broadcast = json.dumps({
                "type": "chat",
                "username": agent.handle,
                "display_name": agent.display_name,
                "message": comment,
                "is_agent": True,
            })
            dead = []
            for ws in _room_connections.get(room_name, []):
                try:
                    await ws.send_text(broadcast)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                _room_connections[room_name].remove(ws)

        finally:
            db.close()
        cycle += 1
