"""
Product-analytics event tracking + admin alerting.

`track_event` is the single entry point. It:
  1. Writes an append-only row to `user_events`.
  2. Emits a structured log line (so events show up in Railway/Sentry too).
  3. For high-signal event types, fires a best-effort admin alert (email).

Design rules:
  - NEVER raise. Analytics must not break the request it's measuring. Every
    failure is swallowed and logged.
  - The caller's DB session is reused so the event commits in the same
    transaction boundary as the action when possible — but we defensively
    commit+rollback our own row so a tracking failure can't poison the
    caller's transaction.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger

log = get_logger(__name__)

# Events worth interrupting a human for. Money in, money out, growth signals.
ALERTABLE_EVENTS = {
    "coins_purchased",        # revenue
    "withdrawal_requested",   # needs admin action (manual payout)
    "subscription_activated", # recurring revenue
}


def track_event(
    db: Session,
    event_type: str,
    *,
    user_id: Optional[int] = None,
    alert: Optional[bool] = None,
    **properties: Any,
) -> None:
    """Record a product event. Best-effort; never raises.

    Args:
        db: the request's SQLAlchemy session.
        event_type: snake_case event name, e.g. "coins_purchased".
        user_id: acting user, or None for anonymous events.
        alert: force-enable/disable the admin alert. Defaults to
               (event_type in ALERTABLE_EVENTS).
        **properties: event-specific fields stored as JSON.
    """
    request_id = _current_request_id()

    # 1. Persist the event row (isolated so a failure can't break the caller).
    try:
        from app.models.user_event import UserEvent

        db.add(UserEvent(
            user_id=user_id,
            event_type=event_type,
            properties=json.dumps(properties, default=str) if properties else None,
            request_id=request_id,
        ))
        db.commit()
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        log.warning("track_event_persist_failed", event_type=event_type, error=str(e))

    # 2. Structured log (always, even if persistence failed).
    log.info("event", event_type=event_type, user_id=user_id, **properties)

    # 3. Admin alert for high-signal events.
    should_alert = alert if alert is not None else (event_type in ALERTABLE_EVENTS)
    if should_alert:
        _send_alert(event_type, user_id=user_id, **properties)


def _current_request_id() -> Optional[str]:
    """Pull the request_id bound by RequestIdMiddleware, if we're in a request."""
    try:
        import structlog
        ctx = structlog.contextvars.get_contextvars()
        return ctx.get("request_id")
    except Exception:
        return None


def _send_alert(event_type: str, *, user_id: Optional[int] = None, **properties: Any) -> None:
    """Best-effort admin alert. Swallows all errors."""
    import os

    if os.getenv("ALERTS_ENABLED", "true").strip().lower() in ("0", "false", "no", "off"):
        return
    try:
        from app.services.email_service import send_admin_alert
        send_admin_alert(event_type, user_id=user_id, **properties)
    except Exception as e:
        log.warning("event_alert_failed", event_type=event_type, error=str(e))
