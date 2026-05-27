"""
P1 — live realtime hardening:
  - WS identity comes from the token, never the client payload (anti-impersonation)
  - anonymous sockets can receive but not send chat
  - blocks persist to live_blocks (durable across restarts)
  - co-host join requests persist to live_join_requests
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

import app.api.v1.live as live_mod
from app.core.security import create_access_token


@pytest.fixture
def point_sessionlocal_at_test_db(db_session, monkeypatch):
    """The WS handler + its helpers call the global SessionLocal directly
    (bypassing the get_db override). Repoint it at the test's in-memory DB so
    WS chat/block reads and writes hit the same data the fixtures seeded."""
    session, TestingSessionLocal = db_session
    monkeypatch.setattr(live_mod, "SessionLocal", TestingSessionLocal)
    # live_chat has no ORM model (created via raw SQL in prod), so create_all
    # didn't make it — build it here so WS chat inserts have somewhere to land.
    session.execute(text(
        "CREATE TABLE IF NOT EXISTS live_chat ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, room_name TEXT, user_id INTEGER, "
        "username TEXT, display_name TEXT, message TEXT, "
        "is_agent BOOLEAN DEFAULT 0, agent_name TEXT, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ))
    session.commit()
    # Clear module-global realtime state so tests don't bleed into each other.
    live_mod._room_connections.clear()
    live_mod._blocked_per_room.clear()
    return TestingSessionLocal


def _token(user_id: int) -> str:
    return create_access_token(subject=str(user_id))


WS = "/api/v1/live/{room}/ws"
BLOCK = "/api/v1/live/{room}/block"
REQUEST_JOIN = "/api/v1/live/{room}/request-join"
ACCEPT_JOIN = "/api/v1/live/{room}/accept-join"
JOIN_REQUESTS = "/api/v1/live/{room}/join-requests"
REACT = "/api/v1/live/{room}/react"


# ---------- reactions (P2) ----------

def test_reaction_requires_auth(client):
    resp = client.post(REACT.format(room="any"), json={"emoji": "❤️"})
    assert resp.status_code in (401, 403)


def test_reaction_broadcasts_allowlisted_emoji(client, make_user, auth_header, monkeypatch):
    captured = []

    async def fake_broadcast(room, payload):
        captured.append((room, payload))

    monkeypatch.setattr(live_mod, "_broadcast", fake_broadcast)
    reactor = make_user(email="rx@example.com", username="reactor")

    resp = client.post(REACT.format(room="scouta-r"), json={"emoji": "🔥"}, headers=auth_header(reactor.id))
    assert resp.status_code == 200
    assert len(captured) == 1
    room, payload = captured[0]
    assert room == "scouta-r"
    assert payload == {"type": "reaction", "emoji": "🔥", "username": "reactor"}


def test_reaction_rejects_unlisted_emoji_falls_back(client, make_user, auth_header, monkeypatch):
    captured = []

    async def fake_broadcast(room, payload):
        captured.append(payload)

    monkeypatch.setattr(live_mod, "_broadcast", fake_broadcast)
    reactor = make_user(email="rx2@example.com", username="reactor2")

    # An arbitrary/unsafe string must not reach clients — falls back to ❤️.
    resp = client.post(
        REACT.format(room="scouta-r2"),
        json={"emoji": "<script>alert(1)</script>"},
        headers=auth_header(reactor.id),
    )
    assert resp.status_code == 200
    assert captured[0]["emoji"] == "❤️"


# ---------- go-live notifications (P2) ----------

def _create_social_tables(session):
    session.execute(text(
        "CREATE TABLE IF NOT EXISTS follows ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, follower_id INTEGER, following_id INTEGER, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ))
    session.execute(text(
        "CREATE TABLE IF NOT EXISTS notifications ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, comment_id INTEGER, "
        "actor_name TEXT, post_id INTEGER, post_title TEXT, read BOOLEAN DEFAULT 0, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ))
    session.commit()


def test_notify_followers_live_inserts_rows(db_session, make_user):
    session, _ = db_session
    _create_social_tables(session)
    host = make_user(email="nh@example.com", username="nhost", display_name="N Host")
    f1 = make_user(email="f1@example.com", username="f1")
    f2 = make_user(email="f2@example.com", username="f2")
    for f in (f1, f2):
        session.execute(
            text("INSERT INTO follows (follower_id, following_id) VALUES (:fid, :hid)"),
            {"fid": f.id, "hid": host.id},
        )
    session.commit()

    live_mod._notify_followers_live(session, host, "scouta-live", "My Show")

    rows = session.execute(
        text("SELECT user_id, type, actor_name, post_title FROM notifications WHERE type='live'")
    ).fetchall()
    assert len(rows) == 2
    assert {r.user_id for r in rows} == {f1.id, f2.id}
    assert all(r.actor_name == "N Host" for r in rows)
    # room_name rides in post_title for deep-linking
    assert all(r.post_title.startswith("scouta-live|") for r in rows)


def test_notify_followers_live_no_followers_no_rows(db_session, make_user):
    session, _ = db_session
    _create_social_tables(session)
    host = make_user(email="nh2@example.com", username="nhost2")

    live_mod._notify_followers_live(session, host, "scouta-live2", "Empty")

    count = session.execute(text("SELECT COUNT(*) FROM notifications")).scalar()
    assert count == 0


def test_notify_followers_live_never_raises(db_session, make_user):
    """No follows table at all → must swallow the error, not raise."""
    session, _ = db_session
    host = make_user(email="nh3@example.com", username="nhost3")
    # Intentionally do NOT create the tables.
    live_mod._notify_followers_live(session, host, "scouta-live3", "X")  # must not raise


# ---------- WS identity / anti-impersonation ----------

def test_ws_identity_valid_token(point_sessionlocal_at_test_db, make_user):
    user = make_user(email="i@example.com", username="ident")

    class FakeWS:
        query_params = {"token": _token(user.id)}

    out = live_mod._ws_identity(FakeWS())
    assert out is not None and out["username"] == "ident" and out["id"] == user.id


def test_ws_identity_no_token_is_anonymous(point_sessionlocal_at_test_db):
    class FakeWS:
        query_params = {}
    assert live_mod._ws_identity(FakeWS()) is None


def test_ws_identity_bad_token_is_anonymous(point_sessionlocal_at_test_db):
    class FakeWS:
        query_params = {"token": "garbage.not.jwt"}
    assert live_mod._ws_identity(FakeWS()) is None


def test_ws_chat_uses_token_identity_not_payload(
    point_sessionlocal_at_test_db, client, make_user, make_stream
):
    """Impersonation guard: a user sends a forged username; the broadcast and
    stored row must use their REAL (token-derived) identity."""
    session = point_sessionlocal_at_test_db()
    attacker = make_user(email="atk@example.com", username="attacker")
    host = make_user(email="hh@example.com", username="hh")
    make_stream("scouta-imp", host.id, status="live")

    with client.websocket_connect(WS.format(room="scouta-imp") + f"?token={_token(attacker.id)}") as ws:
        ws.send_json({"type": "chat", "username": "victim", "display_name": "Victim", "message": "hi"})
        msg = ws.receive_json()

    assert msg["type"] == "chat"
    assert msg["username"] == "attacker"   # NOT "victim"
    assert msg["message"] == "hi"

    row = session.execute(
        text("SELECT username, user_id FROM live_chat WHERE room_name='scouta-imp'")
    ).first()
    assert row.username == "attacker"
    assert row.user_id == attacker.id
    session.close()


def test_ws_anonymous_cannot_send_chat(
    point_sessionlocal_at_test_db, client, make_user, make_stream
):
    session = point_sessionlocal_at_test_db()
    host = make_user(email="anonhost@example.com", username="anonhost")
    make_stream("scouta-anon", host.id, status="live")

    with client.websocket_connect(WS.format(room="scouta-anon")) as ws:  # no token
        ws.send_json({"type": "chat", "username": "ghost", "message": "spam"})
        msg = ws.receive_json()

    assert msg["type"] == "error" and msg["error"] == "auth_required"
    count = session.execute(
        text("SELECT COUNT(*) FROM live_chat WHERE room_name='scouta-anon'")
    ).scalar()
    assert count == 0
    session.close()


# ---------- durable blocks ----------

def test_block_persists_to_db(client, db_session, make_user, make_stream, auth_header):
    session, _ = db_session
    host = make_user(email="bh@example.com", username="bhost")
    make_stream("scouta-blk", host.id, status="live")

    resp = client.post(
        BLOCK.format(room="scouta-blk"),
        json={"username": "troll"},
        headers=auth_header(host.id),
    )
    assert resp.status_code == 200
    row = session.execute(
        text("SELECT room_name, username FROM live_blocks WHERE room_name='scouta-blk'")
    ).first()
    assert row.username == "troll"


def test_block_requires_host(client, make_user, make_stream, auth_header):
    host = make_user(email="bh2@example.com", username="bhost2")
    other = make_user(email="ot@example.com", username="other")
    make_stream("scouta-blk2", host.id, status="live")
    resp = client.post(
        BLOCK.format(room="scouta-blk2"),
        json={"username": "x"},
        headers=auth_header(other.id),
    )
    assert resp.status_code == 403


# ---------- durable join requests ----------

def test_join_request_persists_and_lists(client, db_session, make_user, make_stream, auth_header):
    session, _ = db_session
    host = make_user(email="jh@example.com", username="jhost")
    viewer = make_user(email="jv@example.com", username="jviewer", display_name="JV")
    make_stream("scouta-jr", host.id, status="live")

    r1 = client.post(REQUEST_JOIN.format(room="scouta-jr"), headers=auth_header(viewer.id))
    assert r1.status_code == 200

    # Host lists pending requests (reads from DB, not memory)
    r2 = client.get(JOIN_REQUESTS.format(room="scouta-jr"), headers=auth_header(host.id))
    assert r2.status_code == 200
    reqs = r2.json()["requests"]
    assert len(reqs) == 1 and reqs[0]["username"] == "jviewer"

    row = session.execute(
        text("SELECT COUNT(*) FROM live_join_requests WHERE room_name='scouta-jr'")
    ).scalar()
    assert row == 1


def test_join_request_is_idempotent_per_user(client, db_session, make_user, make_stream, auth_header):
    session, _ = db_session
    host = make_user(email="jh2@example.com", username="jhost2")
    viewer = make_user(email="jv2@example.com", username="jviewer2")
    make_stream("scouta-jr2", host.id, status="live")

    client.post(REQUEST_JOIN.format(room="scouta-jr2"), headers=auth_header(viewer.id))
    client.post(REQUEST_JOIN.format(room="scouta-jr2"), headers=auth_header(viewer.id))

    count = session.execute(
        text("SELECT COUNT(*) FROM live_join_requests WHERE room_name='scouta-jr2'")
    ).scalar()
    assert count == 1  # upsert, not duplicate


def test_reject_join_removes_request(client, db_session, make_user, make_stream, auth_header):
    session, _ = db_session
    host = make_user(email="jh3@example.com", username="jhost3")
    viewer = make_user(email="jv3@example.com", username="jviewer3")
    make_stream("scouta-jr3", host.id, status="live")

    client.post(REQUEST_JOIN.format(room="scouta-jr3"), headers=auth_header(viewer.id))
    resp = client.post(
        ACCEPT_JOIN.format(room="scouta-jr3"),
        json={"username": "jviewer3", "accept": False},
        headers=auth_header(host.id),
    )
    assert resp.status_code == 200
    count = session.execute(
        text("SELECT COUNT(*) FROM live_join_requests WHERE room_name='scouta-jr3'")
    ).scalar()
    assert count == 0
