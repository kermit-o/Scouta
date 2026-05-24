"""
Tests for the product-analytics foundation:
- track_event writes user_events rows + never raises
- alertable events trigger send_admin_alert (mocked)
- /admin/analytics/overview requires superuser + returns the snapshot
- /admin/analytics/users/{id}/activity aggregates existing data + events
"""
from __future__ import annotations

import json
from unittest.mock import patch

from app.models.user_event import UserEvent
from app.models.coin_transaction import CoinTransaction
from app.models.coin_wallet import CoinWallet


OVERVIEW_PATH = "/api/v1/admin/analytics/overview"
ACTIVITY_PATH = "/api/v1/admin/analytics/users/{id}/activity"


# ---------- track_event ----------

def test_track_event_writes_row(db_session, make_user):
    session, _ = db_session
    user = make_user(email="ev@example.com", username="ev")

    from app.services.analytics import track_event
    track_event(session, "user_logged_in", user_id=user.id, username="ev", alert=False)

    row = session.query(UserEvent).filter_by(event_type="user_logged_in").one()
    assert row.user_id == user.id
    assert json.loads(row.properties)["username"] == "ev"


def test_track_event_never_raises_on_bad_session():
    """A broken session must not propagate — analytics can't break requests."""
    from app.services.analytics import track_event

    class BoomSession:
        def add(self, *a, **k):
            raise RuntimeError("db is down")
        def commit(self):
            raise RuntimeError("db is down")
        def rollback(self):
            pass

    # Should swallow everything and return None
    assert track_event(BoomSession(), "user_logged_in", user_id=1, alert=False) is None


@patch("app.services.email_service.send_admin_alert")
def test_alertable_event_fires_alert(mock_alert, db_session, make_user):
    session, _ = db_session
    user = make_user(email="buyer@example.com", username="buyer")

    from app.services.analytics import track_event
    track_event(session, "coins_purchased", user_id=user.id, coins=500, amount_cents=399)

    mock_alert.assert_called_once()
    # event_type passed positionally
    assert mock_alert.call_args.args[0] == "coins_purchased"


@patch("app.services.email_service.send_admin_alert")
def test_non_alertable_event_does_not_fire_alert(mock_alert, db_session, make_user):
    session, _ = db_session
    user = make_user(email="quiet@example.com", username="quiet")

    from app.services.analytics import track_event
    track_event(session, "user_logged_in", user_id=user.id)

    mock_alert.assert_not_called()


# ---------- overview endpoint ----------

def test_overview_requires_superuser(client, make_user, auth_header):
    plain = make_user(email="plain@example.com", username="plain")
    resp = client.get(OVERVIEW_PATH, headers=auth_header(plain.id))
    assert resp.status_code in (401, 403)


def test_overview_returns_snapshot(client, db_session, make_user, make_wallet, auth_header):
    session, _ = db_session
    admin = make_user(email="admin@example.com", username="admin", is_superuser=True)
    u1 = make_user(email="u1@example.com", username="u1")
    u2 = make_user(email="u2@example.com", username="u2")

    # Seed a purchase so revenue shows up
    make_wallet(u1.id, balance=500)
    session.add(CoinTransaction(user_id=u1.id, amount=500, type="purchase", reference_id="cs_1"))
    session.commit()

    resp = client.get(OVERVIEW_PATH, headers=auth_header(admin.id))
    assert resp.status_code == 200
    body = resp.json()

    assert body["users"]["total"] >= 3
    assert body["coins"]["purchased_in_window"] == 500
    assert body["coins"]["purchase_count_in_window"] == 1
    # recent_users newest-first, includes our seeded users
    usernames = {u["username"] for u in body["recent_users"]}
    assert {"u1", "u2", "admin"} <= usernames
    # self-documenting trackable section present
    assert "from_existing_tables_retroactive" in body["trackable"]
    assert "user_registered" in body["trackable"]["from_event_log_going_forward"]


def test_overview_event_breakdown_counts_tracked_events(
    client, db_session, make_user, auth_header
):
    session, _ = db_session
    admin = make_user(email="admin2@example.com", username="admin2", is_superuser=True)
    actor = make_user(email="actor@example.com", username="actor")

    from app.services.analytics import track_event
    track_event(session, "user_logged_in", user_id=actor.id, alert=False)
    track_event(session, "user_logged_in", user_id=actor.id, alert=False)
    track_event(session, "live_started", user_id=actor.id, room="r1", alert=False)

    resp = client.get(OVERVIEW_PATH, headers=auth_header(admin.id))
    assert resp.status_code == 200
    breakdown = resp.json()["event_breakdown"]
    assert breakdown.get("user_logged_in") == 2
    assert breakdown.get("live_started") == 1


# ---------- per-user activity endpoint ----------

def test_user_activity_requires_superuser(client, make_user, auth_header):
    plain = make_user(email="p2@example.com", username="p2")
    resp = client.get(ACTIVITY_PATH.format(id=plain.id), headers=auth_header(plain.id))
    assert resp.status_code in (401, 403)


def test_user_activity_404_on_missing(client, make_user, auth_header):
    admin = make_user(email="admin3@example.com", username="admin3", is_superuser=True)
    resp = client.get(ACTIVITY_PATH.format(id=99999), headers=auth_header(admin.id))
    assert resp.status_code == 404


def test_user_activity_aggregates_existing_data_and_events(
    client, db_session, make_user, make_wallet, auth_header
):
    session, _ = db_session
    admin = make_user(email="admin4@example.com", username="admin4", is_superuser=True)
    target = make_user(email="target@example.com", username="target")

    make_wallet(target.id, balance=300, withdrawable_balance=100, lifetime_earned=400, lifetime_spent=100)
    session.add(CoinTransaction(user_id=target.id, amount=500, type="purchase", reference_id="cs_t"))
    session.commit()

    from app.services.analytics import track_event
    track_event(session, "user_logged_in", user_id=target.id, alert=False)
    track_event(session, "coins_purchased", user_id=target.id, coins=500, alert=False)

    resp = client.get(ACTIVITY_PATH.format(id=target.id), headers=auth_header(admin.id))
    assert resp.status_code == 200
    body = resp.json()

    assert body["user"]["username"] == "target"
    assert body["wallet"]["balance"] == 300
    assert body["wallet"]["withdrawable_balance"] == 100
    assert body["totals"]["coins_purchased"] == 500
    # Event timeline, newest first
    event_types = [e["event_type"] for e in body["recent_events"]]
    assert "user_logged_in" in event_types
    assert "coins_purchased" in event_types
