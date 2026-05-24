"""
Live-stream reconciliation against LiveKit.

LiveKit is the source of truth for who is actually broadcasting. Our
`live_streams.status='live'` flag only flips to 'ended' when the host
explicitly calls /live/{room}/end — so if a host crashes, closes the app, or
loses connection, the row stays 'live' forever (we found one stuck for 11
days). This module closes that gap.

`reconcile_live_streams` lists LiveKit's active rooms and marks as 'ended' any
DB stream that LiveKit no longer knows about (or that has zero publishers,
i.e. the broadcaster is gone and only viewers linger).

SAFETY: if LiveKit is unconfigured or unreachable, we end NOTHING. We must
never kill live streams just because we couldn't reach LiveKit. A young
stream (< GRACE_SECONDS old) is also left alone so a just-started broadcast
has time to connect before we'd consider it orphaned.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.logging import get_logger

log = get_logger(__name__)

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

# A stream younger than this is never reconciled away — gives a fresh
# broadcast time to actually connect to LiveKit before we'd judge it orphaned.
GRACE_SECONDS = int(os.getenv("LIVE_RECONCILE_GRACE_SEC", "120"))


def _as_aware_dt(value) -> datetime | None:
    """Coerce a started_at value to a tz-aware datetime. Postgres hands back a
    datetime; SQLite (tests) hands back a string. Returns None if unparseable."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def _http_url(url: str) -> str:
    """LiveKit's room service speaks HTTP(S); the public URL is usually ws(s)."""
    return url.replace("wss://", "https://").replace("ws://", "http://")


async def _active_livekit_rooms() -> dict[str, int]:
    """Return {room_name: num_publishers} for rooms LiveKit currently knows.

    Raises on any failure so the caller can decide to abort (and NOT end
    streams). A missing/empty result is only trusted when the call succeeds.
    """
    from livekit import api

    lkapi = api.LiveKitAPI(_http_url(LIVEKIT_URL), LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    try:
        res = await lkapi.room.list_rooms(api.ListRoomsRequest())
    finally:
        await lkapi.aclose()
    return {r.name: r.num_publishers for r in res.rooms}


async def reconcile_live_streams(db: Session | None = None) -> dict:
    """End DB live streams that LiveKit no longer has an active broadcast for.

    Returns a summary dict. Never raises — on any error it reports
    skipped/ended=0 so callers (scheduler, admin endpoint) stay simple.
    """
    if not (LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET):
        log.info("live_reconcile_skipped", reason="livekit_not_configured")
        return {"ended": 0, "checked": 0, "skipped": True, "reason": "livekit_not_configured"}

    owns_session = db is None
    db = db or SessionLocal()
    try:
        live_rows = db.execute(text(
            "SELECT room_name, started_at FROM live_streams WHERE status='live'"
        )).fetchall()
        if not live_rows:
            return {"ended": 0, "checked": 0, "skipped": False}

        try:
            active = await _active_livekit_rooms()
        except Exception as e:
            # Could not reach LiveKit → end nothing. Safety over cleanup.
            log.warning("live_reconcile_livekit_unreachable", error=str(e))
            return {"ended": 0, "checked": len(live_rows), "skipped": True, "reason": "livekit_unreachable"}

        now = datetime.now(timezone.utc)
        orphans: list[str] = []
        for row in live_rows:
            room = row.room_name
            started = _as_aware_dt(row.started_at)
            # Respect grace period for freshly started streams.
            if started is not None and now - started < timedelta(seconds=GRACE_SECONDS):
                continue
            publishers = active.get(room)
            # Orphan = LiveKit doesn't know the room, or nobody is publishing.
            if publishers is None or publishers == 0:
                orphans.append(room)

        if orphans:
            stmt = text(
                "UPDATE live_streams SET status='ended', ended_at=CURRENT_TIMESTAMP "
                "WHERE room_name IN :rooms AND status='live'"
            ).bindparams(bindparam("rooms", expanding=True))
            db.execute(stmt, {"rooms": orphans})
            db.commit()
            log.info("live_reconcile_ended", count=len(orphans), rooms=orphans)

        return {"ended": len(orphans), "checked": len(live_rows), "rooms": orphans, "skipped": False}
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        log.error("live_reconcile_failed", error=str(e))
        return {"ended": 0, "checked": 0, "skipped": True, "reason": "error"}
    finally:
        if owns_session:
            db.close()


def reconcile_live_streams_sync(db: Session | None = None) -> dict:
    """Blocking wrapper for the background scheduler thread."""
    import asyncio
    return asyncio.run(reconcile_live_streams(db))


async def force_end_stream(db: Session, room_name: str) -> bool:
    """Admin force-end: flip the DB row to 'ended' and tear down the LiveKit
    room so any lingering participants are disconnected. Returns whether a
    'live' row was found+ended. LiveKit teardown is best-effort."""
    res = db.execute(
        text("UPDATE live_streams SET status='ended', ended_at=CURRENT_TIMESTAMP WHERE room_name=:room AND status='live'"),
        {"room": room_name},
    )
    db.commit()
    ended = res.rowcount > 0

    if LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
        try:
            from livekit import api
            lkapi = api.LiveKitAPI(_http_url(LIVEKIT_URL), LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            try:
                await lkapi.room.delete_room(api.DeleteRoomRequest(room=room_name))
            finally:
                await lkapi.aclose()
        except Exception as e:
            log.warning("force_end_livekit_delete_failed", room=room_name, error=str(e))

    return ended
