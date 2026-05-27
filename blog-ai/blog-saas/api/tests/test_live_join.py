"""
Live-stream /join tests.

Coverage focuses on the access_type matrix for private rooms — the place
where a user pays coins, enters a password, or is screened against an
invite list. Specifically the **paid** path is money-moving (entry fee
credits the host's balance) so it gets the tightest assertions.

Out of scope here: WebSocket broadcasts, LiveKit token contents (token
generation has a local-JWT fallback, so it doesn't need network access
in tests). We only assert that *some* token comes back and that DB
side-effects match the contract.
"""
from __future__ import annotations

import hashlib

import pytest

from app.models.coin_transaction import CoinTransaction
from app.models.coin_wallet import CoinWallet
from app.models.live_stream import LiveStream
from app.models.room_access import RoomAccess


JOIN_PATH = "/api/v1/live/{room}/join"


# ---------- Public room ----------

def test_join_requires_auth(client):
    resp = client.post(JOIN_PATH.format(room="any"), json={})
    assert resp.status_code == 401


def test_join_unknown_stream_returns_404(client, make_user, auth_header):
    user = make_user(email="v1@example.com", username="v1")
    resp = client.post(JOIN_PATH.format(room="ghost"), json={}, headers=auth_header(user.id))
    assert resp.status_code == 404


def test_join_ended_stream_returns_400(client, make_user, make_stream, auth_header):
    host = make_user(email="h0@example.com", username="h0")
    viewer = make_user(email="v0@example.com", username="v0")
    make_stream("dead", host_user_id=host.id, status="ended")
    resp = client.post(JOIN_PATH.format(room="dead"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 400


def test_host_cannot_join_own_stream_returns_409(client, make_user, make_stream, auth_header):
    host = make_user(email="h1@example.com", username="h1")
    make_stream("self", host_user_id=host.id)
    resp = client.post(JOIN_PATH.format(room="self"), json={}, headers=auth_header(host.id))
    assert resp.status_code == 409
    assert "already_broadcasting" in resp.json()["detail"]


def test_join_public_room_returns_token_and_increments_viewer_count(
    client, db_session, make_user, make_stream, auth_header
):
    session, _ = db_session
    host = make_user(email="h2@example.com", username="h2")
    viewer = make_user(email="v2@example.com", username="v2")
    make_stream("hello", host_user_id=host.id, viewer_count=5)

    resp = client.post(JOIN_PATH.format(room="hello"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["token"]
    assert body["title"] == "demo"

    session.expire_all()
    s = session.query(LiveStream).filter_by(room_name="hello").one()
    assert s.viewer_count == 6


# ---------- Paid room ----------

def test_join_paid_room_insufficient_balance_returns_402(
    client, db_session, make_user, make_stream, make_wallet, auth_header
):
    session, _ = db_session
    host = make_user(email="h3@example.com", username="h3")
    viewer = make_user(email="v3@example.com", username="v3")
    make_stream(
        "paywalled",
        host_user_id=host.id,
        is_private=True,
        access_type="paid",
        entry_coin_cost=50,
    )
    make_wallet(viewer.id, balance=10)  # not enough

    resp = client.post(JOIN_PATH.format(room="paywalled"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 402
    assert "paid_entry:50" in resp.json()["detail"]

    # No charge happened, no access granted
    session.expire_all()
    assert session.query(CoinWallet).filter_by(user_id=viewer.id).one().balance == 10
    assert session.query(RoomAccess).filter_by(room_name="paywalled", user_id=viewer.id).first() is None


def test_join_paid_room_charges_viewer_and_credits_host(
    client, db_session, make_user, make_stream, make_wallet, auth_header
):
    """Paid entry: viewer balance debited by cost, host balance + lifetime_earned
    credited by cost, RoomAccess written, two CoinTransaction rows logged."""
    session, _ = db_session
    host = make_user(email="h4@example.com", username="h4")
    viewer = make_user(email="v4@example.com", username="v4")
    make_stream(
        "vip-show",
        host_user_id=host.id,
        is_private=True,
        access_type="paid",
        entry_coin_cost=80,
    )
    make_wallet(viewer.id, balance=200)
    make_wallet(host.id, balance=0, lifetime_earned=0)

    resp = client.post(JOIN_PATH.format(room="vip-show"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 200
    assert resp.json()["token"]

    session.expire_all()

    viewer_wallet = session.query(CoinWallet).filter_by(user_id=viewer.id).one()
    assert viewer_wallet.balance == 200 - 80
    assert viewer_wallet.lifetime_spent == 80

    host_wallet = session.query(CoinWallet).filter_by(user_id=host.id).one()
    # Note: paid entry credits host's BALANCE (not withdrawable_balance) — this
    # matches the current implementation. Gifts go to withdrawable; entries go
    # to balance. If that asymmetry ever changes, this assertion will catch it.
    assert host_wallet.balance == 80
    assert host_wallet.lifetime_earned == 80

    access = session.query(RoomAccess).filter_by(room_name="vip-show", user_id=viewer.id).one()
    assert access.access_type == "paid"

    # Audit ledger: -cost on viewer, +cost on host
    viewer_tx = session.query(CoinTransaction).filter_by(user_id=viewer.id, type="room_entry").one()
    assert viewer_tx.amount == -80
    host_tx = session.query(CoinTransaction).filter_by(user_id=host.id, type="gift_received").one()
    assert host_tx.amount == 80


def test_join_paid_room_idempotent_when_access_already_granted(
    client, db_session, make_user, make_stream, make_wallet, auth_header
):
    """If the viewer already has RoomAccess (re-join), don't charge again.
    This is the protection against double-charging on reconnect."""
    session, _ = db_session
    host = make_user(email="h5@example.com", username="h5")
    viewer = make_user(email="v5@example.com", username="v5")
    make_stream(
        "rejoin-room",
        host_user_id=host.id,
        is_private=True,
        access_type="paid",
        entry_coin_cost=30,
    )
    make_wallet(viewer.id, balance=100)

    # First join: charges 30
    r1 = client.post(JOIN_PATH.format(room="rejoin-room"), json={}, headers=auth_header(viewer.id))
    assert r1.status_code == 200

    # Second join: must NOT charge again
    r2 = client.post(JOIN_PATH.format(room="rejoin-room"), json={}, headers=auth_header(viewer.id))
    assert r2.status_code == 200

    session.expire_all()
    assert session.query(CoinWallet).filter_by(user_id=viewer.id).one().balance == 70  # only one charge
    # One RoomAccess row, two ledger rows total (sender+host from first join)
    assert session.query(RoomAccess).filter_by(room_name="rejoin-room", user_id=viewer.id).count() == 1
    assert session.query(CoinTransaction).filter_by(user_id=viewer.id, type="room_entry").count() == 1


def test_join_paid_room_zero_cost_grants_free_access(
    client, db_session, make_user, make_stream, make_wallet, auth_header
):
    """Edge case: paid room configured with cost=0. No charge, but
    RoomAccess still written so re-joins stay idempotent."""
    session, _ = db_session
    host = make_user(email="h6@example.com", username="h6")
    viewer = make_user(email="v6@example.com", username="v6")
    make_stream(
        "free-paid",
        host_user_id=host.id,
        is_private=True,
        access_type="paid",
        entry_coin_cost=0,
    )
    make_wallet(viewer.id, balance=10)

    resp = client.post(JOIN_PATH.format(room="free-paid"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 200

    session.expire_all()
    assert session.query(CoinWallet).filter_by(user_id=viewer.id).one().balance == 10
    assert session.query(RoomAccess).filter_by(room_name="free-paid", user_id=viewer.id).count() == 1


# ---------- Password room ----------

def test_join_password_room_missing_password_returns_403(
    client, make_user, make_stream, auth_header
):
    host = make_user(email="h7@example.com", username="h7")
    viewer = make_user(email="v7@example.com", username="v7")
    pw_hash = hashlib.sha256(b"hunter22long").hexdigest()
    make_stream(
        "secret",
        host_user_id=host.id,
        is_private=True,
        access_type="password",
        password_hash=pw_hash,
    )
    resp = client.post(JOIN_PATH.format(room="secret"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 403
    assert "password_required" in resp.json()["detail"]


def test_join_password_room_wrong_password_returns_403(
    client, make_user, make_stream, auth_header
):
    host = make_user(email="h8@example.com", username="h8")
    viewer = make_user(email="v8@example.com", username="v8")
    pw_hash = hashlib.sha256(b"correct-pw").hexdigest()
    make_stream(
        "secret2",
        host_user_id=host.id,
        is_private=True,
        access_type="password",
        password_hash=pw_hash,
    )
    resp = client.post(
        JOIN_PATH.format(room="secret2"),
        json={"password": "WRONG"},
        headers=auth_header(viewer.id),
    )
    assert resp.status_code == 403
    assert "wrong_password" in resp.json()["detail"]


def test_join_password_room_correct_password_grants_access(
    client, db_session, make_user, make_stream, auth_header
):
    session, _ = db_session
    host = make_user(email="h9@example.com", username="h9")
    viewer = make_user(email="v9@example.com", username="v9")
    pw_hash = hashlib.sha256(b"correct-pw").hexdigest()
    make_stream(
        "secret3",
        host_user_id=host.id,
        is_private=True,
        access_type="password",
        password_hash=pw_hash,
    )
    resp = client.post(
        JOIN_PATH.format(room="secret3"),
        json={"password": "correct-pw"},
        headers=auth_header(viewer.id),
    )
    assert resp.status_code == 200

    session.expire_all()
    access = session.query(RoomAccess).filter_by(room_name="secret3", user_id=viewer.id).one()
    assert access.access_type == "password_entered"


# ---------- Invite-only ----------

def test_join_invite_only_without_invite_returns_403(
    client, make_user, make_stream, auth_header
):
    host = make_user(email="h10@example.com", username="h10")
    viewer = make_user(email="v10@example.com", username="v10")
    make_stream(
        "vip-invite",
        host_user_id=host.id,
        is_private=True,
        access_type="invite_only",
    )
    resp = client.post(JOIN_PATH.format(room="vip-invite"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 403
    assert "invite_only" in resp.json()["detail"]


def test_join_invite_only_with_existing_room_access_succeeds(
    client, db_session, make_user, make_stream, auth_header
):
    """Pre-seeded RoomAccess (e.g. from an earlier /invite) lets the viewer in."""
    session, _ = db_session
    host = make_user(email="h11@example.com", username="h11")
    viewer = make_user(email="v11@example.com", username="v11")
    make_stream(
        "vip-invite-2",
        host_user_id=host.id,
        is_private=True,
        access_type="invite_only",
    )
    session.add(RoomAccess(room_name="vip-invite-2", user_id=viewer.id, access_type="invited"))
    session.commit()

    resp = client.post(JOIN_PATH.format(room="vip-invite-2"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 200


# ---------- Capacity ----------

def test_join_room_full_returns_403(client, make_user, make_stream, auth_header):
    host = make_user(email="h12@example.com", username="h12")
    viewer = make_user(email="v12@example.com", username="v12")
    make_stream(
        "tiny",
        host_user_id=host.id,
        is_private=True,
        access_type="paid",
        entry_coin_cost=10,
        max_viewer_limit=2,
        viewer_count=2,
    )
    resp = client.post(JOIN_PATH.format(room="tiny"), json={}, headers=auth_header(viewer.id))
    assert resp.status_code == 403
    assert "room_full" in resp.json()["detail"]
