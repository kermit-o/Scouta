from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.message import Conversation, Message
from pydantic import BaseModel
from typing import Dict, List
import json
from datetime import datetime

router = APIRouter(tags=["messages"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, List[WebSocket]] = {}  # user_id -> [ws]

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        if user_id in self.active:
            self.active[user_id] = [w for w in self.active[user_id] if w != ws]

    async def send_to_user(self, user_id: int, data: dict):
        for ws in self.active.get(user_id, []):
            try:
                await ws.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()


def _get_or_create_conversation(db: Session, user1_id: int, user2_id: int) -> Conversation:
    a, b = min(user1_id, user2_id), max(user1_id, user2_id)
    conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == a, Conversation.user2_id == b),
            and_(Conversation.user1_id == b, Conversation.user2_id == a),
        )
    ).first()
    if not conv:
        conv = Conversation(user1_id=a, user2_id=b)
        db.add(conv)
        db.commit()
        db.refresh(conv)
    return conv


def _conv_dict(conv: Conversation, me_id: int, db: Session) -> dict:
    other_id = conv.user2_id if conv.user1_id == me_id else conv.user1_id
    other = db.query(User).filter(User.id == other_id).first()
    unread = db.query(Message).filter(
        Message.conversation_id == conv.id,
        Message.sender_id != me_id,
        Message.read == False,
    ).count()
    return {
        "id": conv.id,
        "other_user": {
            "id": other.id,
            "username": other.username,
            "display_name": other.display_name or other.username,
            "avatar_url": other.avatar_url or "",
        } if other else None,
        "last_message_preview": conv.last_message_preview or "",
        "last_message_at": str(conv.last_message_at) if conv.last_message_at else "",
        "unread": unread,
    }


# ── REST endpoints ──────────────────────────────────────────────

@router.get("/messages/conversations")
def list_conversations(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    convs = db.query(Conversation).filter(
        or_(Conversation.user1_id == me.id, Conversation.user2_id == me.id)
    ).order_by(Conversation.last_message_at.desc()).all()
    return [_conv_dict(c, me.id, db) for c in convs]


@router.get("/messages/conversations/{conv_id}/messages")
def get_messages(conv_id: int, limit: int = 50, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv or (conv.user1_id != me.id and conv.user2_id != me.id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = db.query(Message).filter(Message.conversation_id == conv_id)\
        .order_by(Message.created_at.asc()).limit(limit).all()
    # Marcar como leídos
    for m in msgs:
        if m.sender_id != me.id and not m.read:
            m.read = True
    db.commit()
    return [{"id": m.id, "sender_id": m.sender_id, "body": m.body, "read": m.read, "created_at": str(m.created_at)} for m in msgs]


@router.get("/messages/unread-count")
def unread_count(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    count = db.query(Message).join(Conversation).filter(
        or_(Conversation.user1_id == me.id, Conversation.user2_id == me.id),
        Message.sender_id != me.id,
        Message.read == False,
    ).count()
    return {"unread": count}


@router.post("/messages/start/{username}")
def start_conversation(username: str, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    other = db.query(User).filter(User.username == username).first()
    if not other:
        raise HTTPException(status_code=404, detail="User not found")
    if other.id == me.id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")
    conv = _get_or_create_conversation(db, me.id, other.id)
    return _conv_dict(conv, me.id, db)


# ── WebSocket ────────────────────────────────────────────────────

@router.websocket("/messages/ws/{conv_id}")
async def websocket_chat(conv_id: int, ws: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):
    from app.core.security import decode_token
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
        me = db.query(User).filter(User.id == user_id).first()
        if not me:
            await ws.close(code=4001)
            return
    except Exception:
        await ws.close(code=4001)
        return

    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv or (conv.user1_id != me.id and conv.user2_id != me.id):
        await ws.close(code=4003)
        return

    other_id = conv.user2_id if conv.user1_id == me.id else conv.user1_id
    await manager.connect(me.id, ws)

    try:
        while True:
            data = await ws.receive_text()
            body = data.strip()
            if not body:
                continue

            msg = Message(
                conversation_id=conv_id,
                sender_id=me.id,
                body=body[:2000],
                read=False,
            )
            db.add(msg)
            conv.last_message_preview = body[:100]
            conv.last_message_at = datetime.utcnow()
            db.commit()
            db.refresh(msg)

            payload = {
                "type": "message",
                "id": msg.id,
                "conversation_id": conv_id,
                "sender_id": me.id,
                "sender_username": me.username,
                "sender_avatar": me.avatar_url or "",
                "body": msg.body,
                "created_at": str(msg.created_at),
            }
            # Enviar a ambos usuarios
            await manager.send_to_user(me.id, payload)
            await manager.send_to_user(other_id, {**payload, "type": "new_message"})

    except WebSocketDisconnect:
        manager.disconnect(me.id, ws)
