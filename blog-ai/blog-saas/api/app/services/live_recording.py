"""
Live recording (VOD / replay) via LiveKit Egress → Cloudflare R2.

Opt-in and feature-flagged: nothing records unless BOTH
  - LIVE_RECORDING_ENABLED is truthy (env), AND
  - the host asked to record this specific stream (record=true on start)
This keeps egress + storage cost under explicit control.

All functions are best-effort and NEVER raise — a recording failure must not
break going live, ending a live, or reconciliation. Egress runs on LiveKit's
side and writes the MP4 directly to R2 using the same R2 credentials the app
already uses for thumbnails.

Lifecycle: start_recording (status=recording) → stop_recording
(status=processing) → LiveKit egress webhook marks status=ready with the
playback URL. See handle_egress_webhook.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.logging import get_logger

log = get_logger(__name__)


def recording_enabled() -> bool:
    return os.getenv("LIVE_RECORDING_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")


def _r2_config() -> dict | None:
    """R2 (S3-compatible) config for egress output, or None if incomplete."""
    account = os.getenv("R2_ACCOUNT_ID", "")
    access = os.getenv("R2_ACCESS_KEY_ID", "")
    secret = os.getenv("R2_SECRET_ACCESS_KEY", "")
    bucket = os.getenv("R2_BUCKET", "scouta-media")
    public = os.getenv("R2_PUBLIC_URL", "")
    if not (account and access and secret and bucket and public):
        return None
    return {
        "access": access,
        "secret": secret,
        "bucket": bucket,
        "endpoint": f"https://{account}.r2.cloudflarestorage.com",
        "public": public,
    }


def _lk_env() -> tuple[str, str, str] | None:
    url = os.getenv("LIVEKIT_URL", "")
    key = os.getenv("LIVEKIT_API_KEY", "")
    secret = os.getenv("LIVEKIT_API_SECRET", "")
    if not (url and key and secret):
        return None
    return url.replace("wss://", "https://").replace("ws://", "http://"), key, secret


async def start_recording(room_name: str, host_user_id: int, title: str | None = None) -> dict:
    """Start a LiveKit room-composite egress to R2. Returns a summary dict.
    No-op (skipped) unless recording is enabled and infra is configured."""
    if not recording_enabled():
        return {"started": False, "reason": "recording_disabled"}
    lk = _lk_env()
    r2 = _r2_config()
    if lk is None or r2 is None:
        log.info("recording_skipped", reason="infra_not_configured")
        return {"started": False, "reason": "infra_not_configured"}

    file_key = f"recordings/{room_name}_{int(time.time())}.mp4"
    try:
        from livekit import api

        lk_url, lk_key, lk_secret = lk
        req = api.RoomCompositeEgressRequest(
            room_name=room_name,
            layout="speaker",
            file_outputs=[api.EncodedFileOutput(
                file_type=api.EncodedFileType.MP4,
                filepath=file_key,
                s3=api.S3Upload(
                    access_key=r2["access"],
                    secret=r2["secret"],
                    bucket=r2["bucket"],
                    endpoint=r2["endpoint"],
                    region="auto",
                    force_path_style=True,
                ),
            )],
        )
        lkapi = api.LiveKitAPI(lk_url, lk_key, lk_secret)
        try:
            res = await lkapi.egress.start_room_composite_egress(req)
        finally:
            await lkapi.aclose()
        egress_id = res.egress_id
    except Exception as e:
        log.warning("recording_start_failed", room=room_name, error=str(e))
        return {"started": False, "reason": "egress_error"}

    db = SessionLocal()
    try:
        db.execute(
            text(
                "INSERT INTO live_recordings (room_name, host_user_id, title, egress_id, status, file_key) "
                "VALUES (:room, :host, :title, :eid, 'recording', :fkey)"
            ),
            {"room": room_name, "host": host_user_id, "title": title, "eid": egress_id, "fkey": file_key},
        )
        db.commit()
    except Exception as e:
        log.warning("recording_row_insert_failed", room=room_name, error=str(e))
    finally:
        db.close()

    log.info("recording_started", room=room_name, egress_id=egress_id)
    return {"started": True, "egress_id": egress_id, "file_key": file_key}


async def stop_recording(room_name: str) -> dict:
    """Stop any active egress for a room and mark its recording processing."""
    if not recording_enabled():
        return {"stopped": False, "reason": "recording_disabled"}
    lk = _lk_env()
    if lk is None:
        return {"stopped": False, "reason": "infra_not_configured"}

    db = SessionLocal()
    try:
        row = db.execute(
            text(
                "SELECT egress_id FROM live_recordings "
                "WHERE room_name=:room AND status='recording' ORDER BY id DESC LIMIT 1"
            ),
            {"room": room_name},
        ).first()
        egress_id = row.egress_id if row else None
    except Exception:
        egress_id = None
    finally:
        db.close()

    if not egress_id:
        return {"stopped": False, "reason": "no_active_recording"}

    try:
        from livekit import api
        lk_url, lk_key, lk_secret = lk
        lkapi = api.LiveKitAPI(lk_url, lk_key, lk_secret)
        try:
            await lkapi.egress.stop_egress(api.StopEgressRequest(egress_id=egress_id))
        finally:
            await lkapi.aclose()
    except Exception as e:
        log.warning("recording_stop_failed", room=room_name, egress_id=egress_id, error=str(e))

    db = SessionLocal()
    try:
        db.execute(
            text(
                "UPDATE live_recordings SET status='processing', ended_at=CURRENT_TIMESTAMP "
                "WHERE egress_id=:eid AND status='recording'"
            ),
            {"eid": egress_id},
        )
        db.commit()
    except Exception:
        pass
    finally:
        db.close()

    log.info("recording_stopped", room=room_name, egress_id=egress_id)
    return {"stopped": True, "egress_id": egress_id}


def mark_recording_ready(egress_id: str, file_key: str | None, duration_seconds: int | None) -> bool:
    """Promote a recording to 'ready' with its public playback URL. Called from
    the egress webhook once LiveKit has written the MP4 to R2."""
    r2 = _r2_config()
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT file_key FROM live_recordings WHERE egress_id=:eid"),
            {"eid": egress_id},
        ).first()
        if not row:
            return False
        key = file_key or row.file_key
        playback = f"{r2['public']}/{key}" if (r2 and key) else None
        db.execute(
            text(
                "UPDATE live_recordings SET status='ready', file_key=:fkey, "
                "playback_url=:url, duration_seconds=:dur WHERE egress_id=:eid"
            ),
            {"fkey": key, "url": playback, "dur": duration_seconds, "eid": egress_id},
        )
        db.commit()
        log.info("recording_ready", egress_id=egress_id, playback_url=playback)
        return True
    except Exception as e:
        log.warning("recording_ready_failed", egress_id=egress_id, error=str(e))
        return False
    finally:
        db.close()
