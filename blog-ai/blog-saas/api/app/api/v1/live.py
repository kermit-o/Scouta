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

    # Save to DB
    db.execute(text(
        "INSERT INTO live_streams (room_name, title, host_user_id, org_id, description, status) "
        "VALUES (:room, :title, :uid, 1, :desc, 'live')"
    ), {"room": room_name, "title": title, "uid": user.id, "desc": description})
    db.commit()

    token = _create_livekit_token(room_name, user.display_name or user.username or f"user_{user.id}", can_publish=True)

    return {
        "room_name": room_name,
        "token": token,
        "livekit_url": LIVEKIT_URL,
        "title": title,
    }


@router.post("/live/{room_name}/join")
def join_live(
    room_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Join a live stream as viewer."""
    stream = db.execute(
        text("SELECT id, title, status FROM live_streams WHERE room_name=:room"),
        {"room": room_name}
    ).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    if stream.status != "live":
        raise HTTPException(status_code=400, detail="Stream has ended")

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

    token = _create_livekit_token(room_name, invitee.display_name or invitee.username, can_publish=True)
    return {"token": token, "livekit_url": LIVEKIT_URL, "invited_user": invitee_username}


@router.post("/live/{room_name}/end")
def end_live(
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
            loop = asyncio.get_event_loop()
            loop.create_task(_broadcast_ended())
        except Exception:
            del _room_connections[room_name]
    return {"ok": True}


@router.get("/live/{room_name}/join-anon")
def join_live_anon(room_name: str, db: Session = Depends(get_db)):
    """Join a live stream as anonymous viewer."""
    stream = db.execute(
        text("SELECT id, title, status FROM live_streams WHERE room_name=:room"),
        {"room": room_name}
    ).first()
    if not stream or stream.status != "live":
        raise HTTPException(status_code=404, detail="Stream not found or ended")

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
def request_join(
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
    import asyncio
    async def _broadcast():
        for ws in list(_room_connections.get(room_name, [])):
            try:
                await ws.send_text(request_msg)
            except Exception:
                pass
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(_broadcast())
    except Exception:
        pass
    return {"ok": True, "message": "Request sent to host"}


@router.post("/live/{room_name}/accept-join")
def accept_join(
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
        import asyncio
        async def _broadcast_reject():
            for ws in list(_room_connections.get(room_name, [])):
                try:
                    await ws.send_text(reject_msg)
                except Exception:
                    pass
        try:
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(_broadcast_reject())
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
    import asyncio
    async def _broadcast_accept():
        for ws in list(_room_connections.get(room_name, [])):
            try:
                await ws.send_text(accept_msg)
            except Exception:
                pass
    try:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(_broadcast_accept())
    except Exception:
        pass

    return {"ok": True, "accepted": True, "token": token, "livekit_url": LIVEKIT_URL}


@router.get("/live/active")
def list_active_streams(db: Session = Depends(get_db)):
    """List all active live streams."""
    rows = db.execute(text(
        "SELECT ls.room_name, ls.title, ls.viewer_count, ls.started_at, ls.description, "
        "u.username, u.display_name "
        "FROM live_streams ls JOIN users u ON ls.host_user_id = u.id "
        "WHERE ls.status = 'live' ORDER BY ls.viewer_count DESC LIMIT 20"
    )).fetchall()
    return {"streams": [
        {
            "room_name": r[0], "title": r[1], "viewer_count": r[2],
            "started_at": r[3].isoformat() if r[3] else None,
            "description": r[4],
            "host_username": r[5], "host_display_name": r[6],
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
