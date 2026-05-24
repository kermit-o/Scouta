"""
Tests for live-stream reconciliation + admin force-end.

LiveKit calls are mocked — we never hit a real server. The point is the
DECISION logic: which DB streams get ended, and the safety rules (never end
on LiveKit failure, respect the grace period).
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from sqlalchemy import text

import app.services.live_reconcile as lr


FORCE_END = "/api/v1/admin/live/{room}/end"
RECONCILE = "/api/v1/admin/live/reconcile"


def _age_stream(session, room_name: str, seconds_old: int):
    """Backdate a stream's started_at so it's past the grace period."""
    past = datetime.now(timezone.utc) - timedelta(seconds=seconds_old)
    session.execute(
        text("UPDATE live_streams SET started_at=:t WHERE room_name=:r"),
        {"t": past, "r": room_name},
    )
    session.commit()


def _status(session, room_name: str) -> str:
    return session.execute(
        text("SELECT status FROM live_streams WHERE room_name=:r"), {"r": room_name}
    ).scalar()


# ---------- force_end_stream ----------

def test_force_end_marks_ended(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="h@example.com", username="h")
    make_stream("scouta-aaa", host.id, status="live")

    with patch.object(lr, "LIVEKIT_API_KEY", ""):  # skip LiveKit teardown
        ended = asyncio.run(lr.force_end_stream(session, "scouta-aaa"))

    assert ended is True
    assert _status(session, "scouta-aaa") == "ended"


def test_force_end_returns_false_when_not_live(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="h2@example.com", username="h2")
    make_stream("scouta-bbb", host.id, status="ended")

    with patch.object(lr, "LIVEKIT_API_KEY", ""):
        ended = asyncio.run(lr.force_end_stream(session, "scouta-bbb"))

    assert ended is False


# ---------- reconcile_live_streams ----------

def test_reconcile_skips_when_livekit_unconfigured(db_session):
    session, _ = db_session
    with patch.object(lr, "LIVEKIT_URL", ""):
        result = asyncio.run(lr.reconcile_live_streams(session))
    assert result["skipped"] is True
    assert result["reason"] == "livekit_not_configured"


def test_reconcile_ends_orphan_not_in_livekit(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="o@example.com", username="o")
    make_stream("scouta-orphan", host.id, status="live")
    _age_stream(session, "scouta-orphan", 600)  # well past grace

    # LiveKit knows about NO rooms → the DB stream is orphaned.
    with patch.object(lr, "LIVEKIT_URL", "wss://x"), \
         patch.object(lr, "LIVEKIT_API_KEY", "k"), \
         patch.object(lr, "LIVEKIT_API_SECRET", "s"), \
         patch.object(lr, "_active_livekit_rooms", AsyncMock(return_value={})):
        result = asyncio.run(lr.reconcile_live_streams(session))

    assert result["ended"] == 1
    assert _status(session, "scouta-orphan") == "ended"


def test_reconcile_keeps_actively_publishing_stream(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="a@example.com", username="a")
    make_stream("scouta-active", host.id, status="live")
    _age_stream(session, "scouta-active", 600)

    # LiveKit reports 1 publisher → still broadcasting, must NOT end.
    with patch.object(lr, "LIVEKIT_URL", "wss://x"), \
         patch.object(lr, "LIVEKIT_API_KEY", "k"), \
         patch.object(lr, "LIVEKIT_API_SECRET", "s"), \
         patch.object(lr, "_active_livekit_rooms", AsyncMock(return_value={"scouta-active": 1})):
        result = asyncio.run(lr.reconcile_live_streams(session))

    assert result["ended"] == 0
    assert _status(session, "scouta-active") == "live"


def test_reconcile_ends_room_with_zero_publishers(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="z@example.com", username="z")
    make_stream("scouta-empty", host.id, status="live")
    _age_stream(session, "scouta-empty", 600)

    # Room exists in LiveKit but nobody is publishing → host gone, end it.
    with patch.object(lr, "LIVEKIT_URL", "wss://x"), \
         patch.object(lr, "LIVEKIT_API_KEY", "k"), \
         patch.object(lr, "LIVEKIT_API_SECRET", "s"), \
         patch.object(lr, "_active_livekit_rooms", AsyncMock(return_value={"scouta-empty": 0})):
        result = asyncio.run(lr.reconcile_live_streams(session))

    assert result["ended"] == 1
    assert _status(session, "scouta-empty") == "ended"


def test_reconcile_respects_grace_period(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="g@example.com", username="g")
    make_stream("scouta-fresh", host.id, status="live")  # started_at = now()

    # Even though LiveKit knows no rooms, a just-started stream is left alone.
    with patch.object(lr, "LIVEKIT_URL", "wss://x"), \
         patch.object(lr, "LIVEKIT_API_KEY", "k"), \
         patch.object(lr, "LIVEKIT_API_SECRET", "s"), \
         patch.object(lr, "_active_livekit_rooms", AsyncMock(return_value={})):
        result = asyncio.run(lr.reconcile_live_streams(session))

    assert result["ended"] == 0
    assert _status(session, "scouta-fresh") == "live"


def test_reconcile_ends_nothing_when_livekit_unreachable(db_session, make_user, make_stream):
    session, _ = db_session
    host = make_user(email="u@example.com", username="u")
    make_stream("scouta-unreach", host.id, status="live")
    _age_stream(session, "scouta-unreach", 600)

    # LiveKit call raises → we must NOT end any stream.
    with patch.object(lr, "LIVEKIT_URL", "wss://x"), \
         patch.object(lr, "LIVEKIT_API_KEY", "k"), \
         patch.object(lr, "LIVEKIT_API_SECRET", "s"), \
         patch.object(lr, "_active_livekit_rooms", AsyncMock(side_effect=RuntimeError("boom"))):
        result = asyncio.run(lr.reconcile_live_streams(session))

    assert result["ended"] == 0
    assert result["skipped"] is True
    assert _status(session, "scouta-unreach") == "live"


# ---------- admin endpoints ----------

def test_admin_force_end_requires_superuser(client, make_user, make_stream, auth_header):
    plain = make_user(email="p@example.com", username="p")
    make_stream("scouta-x", plain.id, status="live")
    resp = client.post(FORCE_END.format(room="scouta-x"), headers=auth_header(plain.id))
    assert resp.status_code in (401, 403)


def test_admin_force_end_404_when_no_live(client, make_user, auth_header):
    admin = make_user(email="adm@example.com", username="adm", is_superuser=True)
    with patch.object(lr, "LIVEKIT_API_KEY", ""):
        resp = client.post(FORCE_END.format(room="nope"), headers=auth_header(admin.id))
    assert resp.status_code == 404


def test_admin_force_end_ends_stream(client, db_session, make_user, make_stream, auth_header):
    session, _ = db_session
    admin = make_user(email="adm2@example.com", username="adm2", is_superuser=True)
    streamer = make_user(email="str@example.com", username="str")
    make_stream("scouta-kill", streamer.id, status="live")

    with patch.object(lr, "LIVEKIT_API_KEY", ""):
        resp = client.post(FORCE_END.format(room="scouta-kill"), headers=auth_header(admin.id))

    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert _status(session, "scouta-kill") == "ended"


def test_admin_reconcile_requires_superuser(client, make_user, auth_header):
    plain = make_user(email="p3@example.com", username="p3")
    resp = client.post(RECONCILE, headers=auth_header(plain.id))
    assert resp.status_code in (401, 403)


def test_admin_reconcile_returns_summary(client, make_user, auth_header):
    admin = make_user(email="adm3@example.com", username="adm3", is_superuser=True)
    with patch.object(lr, "LIVEKIT_URL", ""):  # unconfigured → skipped summary
        resp = client.post(RECONCILE, headers=auth_header(admin.id))
    assert resp.status_code == 200
    assert resp.json()["skipped"] is True
