"""
Live streaming via LiveKit
"""
import os
import time
import random
import string
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.user import User
from typing import Optional
import json
import asyncio

router = APIRouter()

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://scouta-pi70lg8z.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIb89yuTt3jXAH")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "AiUeExsGHO2zSAfL9O4eXMGQm07qZjCWB9uWUH5vFh2A")


def _gen_room_name() -> str:
    return "scouta-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def _create_livekit_token(room_name: str, participant_name: str, can_publish: bool = False) -> str:
    """Generate a LiveKit JWT token."""
    try:
        from livekit.api import AccessToken, VideoGrants
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=can_publish,
            can_subscribe=True,
            can_publish_data=True,
        ))
        return token.to_jwt()
    except Exception as e:
        # Fallback: manual JWT
        import hmac, hashlib, base64
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b'=').decode()
        payload = {
            "iss": LIVEKIT_API_KEY,
            "sub": participant_name,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600 * 6,
            "video": {"room": room_name, "roomJoin": True, "canPublish": can_publish, "canSubscribe": True}
        }
        import base64 as b64
        payload_b64 = b64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        sig_input = f"{header}.{payload_b64}"
        sig = hmac.new(LIVEKIT_API_SECRET.encode(), sig_input.encode(), hashlib.sha256).digest()
        sig_b64 = b64.urlsafe_b64encode(sig).rstrip(b'=').decode()
        return f"{sig_input}.{sig_b64}"


# ── WebSocket connections per room ────────────────────────────────────
_room_connections: dict[str, list[WebSocket]] = {}
# ── Pending join requests per room ────────────────────────────────────
_join_requests: dict[str, list[dict]] = {}


@router.post("/live/start")
def start_live(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Start a live stream — creates room and returns token."""
    title = payload.get("title", "Live Stream").strip()
    description = payload.get("description", "")
    if not title:
        raise HTTPException(status_code=400, detail="Title required")

    # Terminar cualquier live anterior del mismo usuario
    db.execute(text(
        "UPDATE live_streams SET status='ended', ended_at=NOW() WHERE host_user_id=:uid AND status='live'"
    ), {"uid": user.id})
    db.commit()

    room_name = _gen_room_name()

    # Private room settings
    is_private = payload.get("is_private", False)
    access_type = payload.get("access_type", "public")  # public, password, invite_only, paid
    entry_coin_cost = int(payload.get("entry_coin_cost", 0))
    max_viewer_limit = int(payload.get("max_viewer_limit", 0))
    password = payload.get("password", "")

    password_hash = None
    if is_private and access_type == "password" and password:
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Save to DB
    db.execute(text(
        "INSERT INTO live_streams (room_name, title, host_user_id, org_id, description, status, "
        "is_private, password_hash, access_type, entry_coin_cost, max_viewer_limit) "
        "VALUES (:room, :title, :uid, 1, :desc, 'live', "
        ":is_private, :pw_hash, :access_type, :entry_cost, :max_limit)"
    ), {
        "room": room_name, "title": title, "uid": user.id, "desc": description,
        "is_private": is_private, "pw_hash": password_hash, "access_type": access_type if is_private else "public",
        "entry_cost": entry_coin_cost if is_private else 0, "max_limit": max_viewer_limit,
    })
    db.commit()

    token = _create_livekit_token(room_name, user.display_name or user.username or f"user_{user.id}", can_publish=True)

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

    # Host always has access
    if stream.host_user_id != user.id and stream.is_private:
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
                    # Deduct coins
                    wallet.balance -= cost
                    wallet.lifetime_spent += cost
                    # Credit host
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

    token = _create_livekit_token(room_name, user.display_name or user.username or f"user_{user.id}", can_publish=False)

    # Update viewer count
    db.execute(text("UPDATE live_streams SET viewer_count = viewer_count + 1 WHERE room_name=:room"), {"room": room_name})
    db.commit()

    return {"token": token, "livekit_url": LIVEKIT_URL, "title": stream.title}


@router.post("/live/{room_name}/invite")
def invite_to_live(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Invite another user to publish (duo/group live)."""
    invitee_username = payload.get("username")
    invitee = db.query(User).filter(User.username == invitee_username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")

    # Also grant room access for private rooms
    from app.models.room_access import RoomAccess
    existing = db.query(RoomAccess).filter(RoomAccess.room_name == room_name, RoomAccess.user_id == invitee.id).first()
    if not existing:
        db.add(RoomAccess(room_name=room_name, user_id=invitee.id, access_type="invited"))
        db.commit()

    token = _create_livekit_token(room_name, invitee.display_name or invitee.username, can_publish=True)
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

    # Verify caller is host
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
    """End a live stream."""
    db.execute(text(
        "UPDATE live_streams SET status='ended', ended_at=NOW() WHERE room_name=:room"
    ), {"room": room_name})
    db.commit()
    # Broadcast stream ended to all viewers
    if room_name in _room_connections:
        import asyncio
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

    import random, string
    anon_name = "viewer_" + "".join(random.choices(string.ascii_lowercase, k=6))
    token = _create_livekit_token(room_name, anon_name, can_publish=False)
    db.execute(text("UPDATE live_streams SET viewer_count = viewer_count + 1 WHERE room_name=:room"), {"room": room_name})
    db.commit()
    return {"token": token, "livekit_url": LIVEKIT_URL, "title": stream.title}


@router.post("/live/{room_name}/block")
def block_from_live(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host blocks a user from the live chat."""
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    # Broadcast block to room — viewer will be disconnected
    if room_name in _room_connections:
        block_msg = json.dumps({"type": "blocked", "username": username})
        # Store blocked users per room (in memory)
        if not hasattr(_room_connections, "_blocked"):
            _room_connections["_blocked"] = {}
        _room_connections["_blocked"][room_name] = _room_connections.get("_blocked_" + room_name, set())
        _room_connections["_blocked_" + room_name] = _room_connections.get("_blocked_" + room_name, set())
        _room_connections["_blocked_" + room_name].add(username)
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

    # Broadcast join request to host via WebSocket
    request_msg = json.dumps({
        "type": "join_request",
        "username": user.username,
        "display_name": user.display_name or user.username,
        "user_id": user.id,
        "room_name": room_name,
    })
    # Store request for polling
    if room_name not in _join_requests:
        _join_requests[room_name] = []
    # Avoid duplicates
    existing = [r for r in _join_requests[room_name] if r["username"] != user.username]
    _join_requests[room_name] = existing + [{"username": user.username, "display_name": user.display_name or user.username, "user_id": user.id}]

    for ws in list(_room_connections.get(room_name, [])):
        try:
            await ws.send_text(request_msg)
        except Exception:
            pass
    return {"ok": True, "message": "Request sent to host"}


@router.post("/live/{room_name}/accept-join")
async def accept_join(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host accepts a join request — returns publisher token for the requester."""
    username = payload.get("username")
    accept = payload.get("accept", True)

    if not accept:
        # Broadcast rejection
        reject_msg = json.dumps({
            "type": "join_rejected",
            "username": username,
        })
        if room_name in _join_requests:
            _join_requests[room_name] = [r for r in _join_requests[room_name] if r["username"] != username]
        for ws in list(_room_connections.get(room_name, [])):
            try:
                await ws.send_text(reject_msg)
            except Exception:
                pass
        return {"ok": True, "accepted": False}

    # Generate publisher token for the invitee
    invitee = db.query(User).filter(User.username == username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")

    token = _create_livekit_token(room_name, invitee.display_name or invitee.username, can_publish=True)

    # Broadcast accepted with token
    accept_msg = json.dumps({
        "type": "join_accepted",
        "username": username,
        "token": token,
        "livekit_url": LIVEKIT_URL,
        "room_name": room_name,
    })
    if room_name in _join_requests:
        _join_requests[room_name] = [r for r in _join_requests[room_name] if r["username"] != username]
    for ws in list(_room_connections.get(room_name, [])):
        try:
            await ws.send_text(accept_msg)
        except Exception:
            pass
    return {"ok": True, "accepted": True, "token": token, "livekit_url": LIVEKIT_URL}


@router.post("/live/{room_name}/kick")
async def kick_from_live(
    room_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Host kicks a co-host from the live."""
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
    # Update viewer count
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
    requests = _join_requests.get(room_name, [])
    return {"requests": requests}


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

    # Validate gift exists
    gift = db.query(GiftCatalog).filter(GiftCatalog.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    # Validate stream is live and get host
    stream = db.execute(
        text("SELECT id, host_user_id, status FROM live_streams WHERE room_name=:room"),
        {"room": room_name}
    ).first()
    if not stream or stream.status != "live":
        raise HTTPException(status_code=404, detail="Stream not found or ended")
    if stream.host_user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot gift yourself")

    host_user_id = stream.host_user_id

    # Check sender balance
    sender_wallet = db.query(CoinWallet).filter(CoinWallet.user_id == user.id).first()
    if not sender_wallet or sender_wallet.balance < gift.coin_cost:
        raise HTTPException(status_code=402, detail="Insufficient coins")

    # Get or create host wallet
    host_wallet = db.query(CoinWallet).filter(CoinWallet.user_id == host_user_id).first()
    if not host_wallet:
        host_wallet = CoinWallet(user_id=host_user_id, balance=0)
        db.add(host_wallet)
        db.flush()

    # Atomic transfer with 80/20 commission split
    PLATFORM_FEE = 0.20
    fee_amount = max(1, int(gift.coin_cost * PLATFORM_FEE)) if gift.coin_cost >= 5 else 0
    host_amount = gift.coin_cost - fee_amount

    sender_wallet.balance -= gift.coin_cost
    sender_wallet.lifetime_spent += gift.coin_cost
    host_wallet.withdrawable_balance += host_amount  # host earns 80% as withdrawable
    host_wallet.lifetime_earned += host_amount

    # Record gift send
    gift_send = GiftSend(
        stream_room_name=room_name,
        sender_user_id=user.id,
        recipient_user_id=host_user_id,
        gift_id=gift.id,
        coin_amount=gift.coin_cost,
    )
    db.add(gift_send)
    db.flush()  # get gift_send.id

    # Record platform earnings
    from app.models.platform_earnings import PlatformEarnings
    db.add(PlatformEarnings(
        stream_room_name=room_name,
        gift_send_id=gift_send.id,
        amount=gift.coin_cost,
        fee_amount=fee_amount,
        host_amount=host_amount,
    ))

    # Record transactions
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

    # Broadcast gift to all viewers via WebSocket
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
        "u.username, u.display_name, ls.is_private, ls.access_type, ls.entry_coin_cost "
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
@router.websocket("/live/{room_name}/ws")
async def live_chat_ws(websocket: WebSocket, room_name: str):
    await websocket.accept()
    if room_name not in _room_connections:
        _room_connections[room_name] = []
    _room_connections[room_name].append(websocket)

    # Start AI agent commenter if first connection
    if len(_room_connections[room_name]) == 1:
        asyncio.create_task(_ai_agent_loop(room_name))

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            # Broadcast to all in room
            db = SessionLocal()
            try:
                db.execute(text(
                    "INSERT INTO live_chat (room_name, user_id, username, display_name, message) "
                    "VALUES (:room, :uid, :uname, :dname, :msg)"
                ), {"room": room_name, "uid": msg.get("user_id"), "uname": msg.get("username"),
                    "dname": msg.get("display_name"), "msg": msg.get("message", "")})
                db.commit()
            finally:
                db.close()

            broadcast = json.dumps({
                "type": "chat",
                "username": msg.get("username"),
                "display_name": msg.get("display_name"),
                "message": msg.get("message"),
                "is_agent": False,
            })
            dead = []
            for ws in _room_connections.get(room_name, []):
                try:
                    await ws.send_text(broadcast)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                _room_connections[room_name].remove(ws)

    except WebSocketDisconnect:
        if websocket in _room_connections.get(room_name, []):
            _room_connections[room_name].remove(websocket)


async def _ai_agent_loop(room_name: str):
    """AI agents comment every 30s on the live stream."""
    await asyncio.sleep(15)
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
        await asyncio.sleep(30)
        if not _room_connections.get(room_name):
            break

        db = SessionLocal()
        try:
            # Check stream still live
            still_live = db.execute(
                text("SELECT status FROM live_streams WHERE room_name=:room"),
                {"room": room_name}
            ).first()
            if not still_live or still_live[0] != "live":
                break

            # Pick random agent
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

            # Save to DB
            db.execute(text(
                "INSERT INTO live_chat (room_name, message, is_agent, agent_name) "
                "VALUES (:room, :msg, TRUE, :aname)"
            ), {"room": room_name, "msg": comment, "aname": agent.display_name})
            db.commit()

            # Broadcast
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
