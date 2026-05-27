"""
P3 — live recording / replay (VOD via LiveKit Egress → R2).

Feature is opt-in + flag-gated (LIVE_RECORDING_ENABLED). LiveKit egress calls
are mocked; we test the gating, DB lifecycle, and the recordings listing.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from sqlalchemy import text

import app.services.live_recording as rec


@pytest.fixture
def rec_db(db_session, monkeypatch):
    """Point the recording service's SessionLocal at the test DB."""
    session, TestingSessionLocal = db_session
    monkeypatch.setattr(rec, "SessionLocal", TestingSessionLocal)
    return session, TestingSessionLocal


def _enable_recording(monkeypatch):
    monkeypatch.setenv("LIVE_RECORDING_ENABLED", "true")
    monkeypatch.setenv("LIVEKIT_URL", "wss://x.livekit.cloud")
    monkeypatch.setenv("LIVEKIT_API_KEY", "k")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "s")
    monkeypatch.setenv("R2_ACCOUNT_ID", "acct")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "ak")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "sk")
    monkeypatch.setenv("R2_BUCKET", "scouta-media")
    monkeypatch.setenv("R2_PUBLIC_URL", "https://pub.r2.dev")


class _FakeEgress:
    async def start_room_composite_egress(self, req):
        return SimpleNamespace(egress_id="EG_TEST")

    async def stop_egress(self, req):
        return None


class _FakeLKAPI:
    def __init__(self, *a, **k):
        self.egress = _FakeEgress()

    async def aclose(self):
        pass


# ---------- gating ----------

def test_recording_disabled_by_default(monkeypatch):
    monkeypatch.delenv("LIVE_RECORDING_ENABLED", raising=False)
    assert rec.recording_enabled() is False


def test_start_recording_noop_when_disabled(rec_db, monkeypatch):
    monkeypatch.setenv("LIVE_RECORDING_ENABLED", "false")
    out = asyncio.run(rec.start_recording("scouta-x", host_user_id=1))
    assert out["started"] is False and out["reason"] == "recording_disabled"


def test_start_recording_noop_when_infra_missing(rec_db, monkeypatch):
    monkeypatch.setenv("LIVE_RECORDING_ENABLED", "true")
    monkeypatch.delenv("LIVEKIT_URL", raising=False)
    monkeypatch.delenv("R2_ACCOUNT_ID", raising=False)
    out = asyncio.run(rec.start_recording("scouta-x", host_user_id=1))
    assert out["started"] is False and out["reason"] == "infra_not_configured"


# ---------- lifecycle ----------

def test_start_recording_inserts_row(rec_db, make_user, monkeypatch):
    session, _ = rec_db
    _enable_recording(monkeypatch)
    host = make_user(email="rh@example.com", username="rhost")

    with patch("livekit.api.LiveKitAPI", _FakeLKAPI):
        out = asyncio.run(rec.start_recording("scouta-rec", host.id, "My Show"))

    assert out["started"] is True and out["egress_id"] == "EG_TEST"
    row = session.execute(
        text("SELECT room_name, status, egress_id, host_user_id FROM live_recordings WHERE room_name='scouta-rec'")
    ).first()
    assert row.status == "recording"
    assert row.egress_id == "EG_TEST"
    assert row.host_user_id == host.id


def test_stop_recording_marks_processing(rec_db, make_user, monkeypatch):
    session, _ = rec_db
    _enable_recording(monkeypatch)
    host = make_user(email="rh2@example.com", username="rhost2")

    with patch("livekit.api.LiveKitAPI", _FakeLKAPI):
        asyncio.run(rec.start_recording("scouta-rec2", host.id))
        out = asyncio.run(rec.stop_recording("scouta-rec2"))

    assert out["stopped"] is True
    status = session.execute(
        text("SELECT status FROM live_recordings WHERE room_name='scouta-rec2'")
    ).scalar()
    assert status == "processing"


def test_mark_recording_ready_sets_playback_url(rec_db, make_user, monkeypatch):
    session, _ = rec_db
    _enable_recording(monkeypatch)
    host = make_user(email="rh3@example.com", username="rhost3")
    with patch("livekit.api.LiveKitAPI", _FakeLKAPI):
        asyncio.run(rec.start_recording("scouta-rec3", host.id))

    ok = rec.mark_recording_ready("EG_TEST", file_key="recordings/scouta-rec3_1.mp4", duration_seconds=120)
    assert ok is True
    row = session.execute(
        text("SELECT status, playback_url, duration_seconds FROM live_recordings WHERE egress_id='EG_TEST'")
    ).first()
    assert row.status == "ready"
    assert row.playback_url == "https://pub.r2.dev/recordings/scouta-rec3_1.mp4"
    assert row.duration_seconds == 120


# ---------- listing endpoint ----------

def test_list_recordings_returns_only_ready(client, db_session, make_user):
    session, _ = db_session
    host = make_user(email="lr@example.com", username="lrhost")
    # one ready, one still processing
    session.execute(text(
        "INSERT INTO live_recordings (room_name, host_user_id, title, status, playback_url) "
        "VALUES ('r-ready', :h, 'Ready One', 'ready', 'https://pub.r2.dev/r1.mp4')"
    ), {"h": host.id})
    session.execute(text(
        "INSERT INTO live_recordings (room_name, host_user_id, title, status, playback_url) "
        "VALUES ('r-proc', :h, 'Processing', 'processing', NULL)"
    ), {"h": host.id})
    session.commit()

    resp = client.get("/api/v1/live/recordings")
    assert resp.status_code == 200
    recs = resp.json()["recordings"]
    assert len(recs) == 1
    assert recs[0]["title"] == "Ready One"
    assert recs[0]["playback_url"] == "https://pub.r2.dev/r1.mp4"
    assert recs[0]["host_username"] == "lrhost"


def test_list_recordings_filters_by_user(client, db_session, make_user):
    session, _ = db_session
    h1 = make_user(email="lr1@example.com", username="lr1")
    h2 = make_user(email="lr2@example.com", username="lr2")
    for h, room in ((h1, "ra"), (h2, "rb")):
        session.execute(text(
            "INSERT INTO live_recordings (room_name, host_user_id, status, playback_url) "
            "VALUES (:room, :h, 'ready', 'https://pub.r2.dev/x.mp4')"
        ), {"room": room, "h": h.id})
    session.commit()

    resp = client.get(f"/api/v1/live/recordings?user_id={h2.id}")
    assert resp.status_code == 200
    recs = resp.json()["recordings"]
    assert len(recs) == 1 and recs[0]["host_user_id"] == h2.id


# ---------- egress webhook auth ----------

def test_egress_webhook_rejects_bad_signature(client):
    resp = client.post(
        "/api/v1/live/egress-webhook",
        content=b'{"event":"egress_ended"}',
        headers={"Authorization": "bogus"},
    )
    assert resp.status_code == 401
