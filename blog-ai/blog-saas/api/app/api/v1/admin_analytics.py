"""
Admin analytics — read-only views over users and their activity.

Two endpoints, both require_superuser:
  GET /admin/analytics/overview          platform snapshot + recent signups
  GET /admin/analytics/users/{id}/activity   one user's full activity trail

Everything here aggregates data we ALREADY store (users, posts, comments,
coin_transactions, gift_sends, live_streams, withdrawal_requests) plus the
new user_events log. The existing-table aggregates work retroactively for
users who signed up before event tracking existed; user_events fills in
behavioural events (logins, live joins) going forward.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_superuser
from app.models.user import User
from app.models.coin_transaction import CoinTransaction
from app.models.coin_wallet import CoinWallet
from app.models.gift import GiftSend
from app.models.live_stream import LiveStream
from app.models.withdrawal_request import WithdrawalRequest
from app.models.user_event import UserEvent

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


def _since(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


@router.get("/overview")
def overview(
    days: int = Query(default=30, ge=1, le=365),
    _: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):
    since = _since(days)

    total_users = db.query(func.count(User.id)).scalar() or 0
    new_users = db.query(func.count(User.id)).filter(User.created_at >= since).scalar() or 0
    verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar() or 0

    active_streams = db.query(func.count(LiveStream.id)).filter(LiveStream.status == "live").scalar() or 0
    streams_in_window = db.query(func.count(LiveStream.id)).filter(LiveStream.started_at >= since).scalar() or 0

    # Revenue proxy: coins purchased (type='purchase') in window
    coins_purchased = db.query(func.coalesce(func.sum(CoinTransaction.amount), 0)).filter(
        CoinTransaction.type == "purchase",
        CoinTransaction.created_at >= since,
    ).scalar() or 0
    purchase_count = db.query(func.count(CoinTransaction.id)).filter(
        CoinTransaction.type == "purchase",
        CoinTransaction.created_at >= since,
    ).scalar() or 0

    gifts_sent = db.query(func.count(GiftSend.id)).filter(GiftSend.created_at >= since).scalar() or 0
    pending_withdrawals = db.query(func.count(WithdrawalRequest.id)).filter(
        WithdrawalRequest.status.in_(["pending", "processing"])
    ).scalar() or 0

    # Recent signups, newest first
    recent = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(50)
        .all()
    )
    recent_users = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "display_name": u.display_name,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in recent
    ]

    # Event-type breakdown (only populated once tracking has been deployed)
    event_breakdown = dict(
        db.query(UserEvent.event_type, func.count(UserEvent.id))
        .filter(UserEvent.created_at >= since)
        .group_by(UserEvent.event_type)
        .all()
    )

    return {
        "window_days": days,
        "users": {
            "total": total_users,
            "new_in_window": new_users,
            "verified": verified_users,
        },
        "live": {
            "active_now": active_streams,
            "started_in_window": streams_in_window,
        },
        "coins": {
            "purchased_in_window": coins_purchased,
            "purchase_count_in_window": purchase_count,
            "gifts_sent_in_window": gifts_sent,
            "pending_withdrawals": pending_withdrawals,
        },
        "event_breakdown": event_breakdown,
        "recent_users": recent_users,
        # Self-documenting: what this platform can currently track per user.
        "trackable": _TRACKABLE,
    }


@router.get("/users/{user_id}/activity")
def user_activity(
    user_id: int,
    _: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    wallet = db.query(CoinWallet).filter(CoinWallet.user_id == user_id).first()

    posts_count = db.execute(
        text("SELECT COUNT(*) FROM posts WHERE author_user_id = :uid"), {"uid": user_id}
    ).scalar() or 0
    comments_count = db.execute(
        text("SELECT COUNT(*) FROM comments WHERE author_user_id = :uid"), {"uid": user_id}
    ).scalar() or 0

    coins_purchased = db.query(func.coalesce(func.sum(CoinTransaction.amount), 0)).filter(
        CoinTransaction.user_id == user_id, CoinTransaction.type == "purchase"
    ).scalar() or 0
    gifts_sent = db.query(func.count(GiftSend.id)).filter(GiftSend.sender_user_id == user_id).scalar() or 0
    gifts_received = db.query(func.count(GiftSend.id)).filter(GiftSend.recipient_user_id == user_id).scalar() or 0
    streams_hosted = db.query(func.count(LiveStream.id)).filter(LiveStream.host_user_id == user_id).scalar() or 0
    withdrawals = db.query(func.count(WithdrawalRequest.id)).filter(WithdrawalRequest.user_id == user_id).scalar() or 0

    # Recent behavioural events
    events = (
        db.query(UserEvent)
        .filter(UserEvent.user_id == user_id)
        .order_by(UserEvent.created_at.desc())
        .limit(100)
        .all()
    )
    timeline = [
        {
            "event_type": e.event_type,
            "properties": json.loads(e.properties) if e.properties else {},
            "request_id": e.request_id,
            "at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "is_verified": user.is_verified,
            "is_banned": getattr(user, "is_banned", False),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "wallet": {
            "balance": wallet.balance if wallet else 0,
            "withdrawable_balance": wallet.withdrawable_balance if wallet else 0,
            "lifetime_earned": wallet.lifetime_earned if wallet else 0,
            "lifetime_spent": wallet.lifetime_spent if wallet else 0,
        },
        "totals": {
            "posts": posts_count,
            "comments": comments_count,
            "coins_purchased": coins_purchased,
            "gifts_sent": gifts_sent,
            "gifts_received": gifts_received,
            "streams_hosted": streams_hosted,
            "withdrawals": withdrawals,
        },
        "recent_events": timeline,
    }


# What the platform can currently track for a user, surfaced in /overview so
# the answer to "what can we measure?" lives next to the data.
_TRACKABLE = {
    "from_existing_tables_retroactive": [
        "signup date + verification status (users)",
        "posts authored (posts)",
        "comments authored (comments)",
        "coins purchased + balance + lifetime earned/spent (coin_wallets, coin_transactions)",
        "gifts sent / received (gift_sends)",
        "live streams hosted (live_streams)",
        "withdrawal requests + status (withdrawal_requests)",
        "subscription plan + status (subscriptions)",
    ],
    "from_event_log_going_forward": [
        "user_registered",
        "user_logged_in",
        "live_started",
        "live_joined (with access_type: public/paid/password/invite)",
        "coins_purchased",
        "gift_sent",
        "withdrawal_requested",
        "subscription_activated",
    ],
}
