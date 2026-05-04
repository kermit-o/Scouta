"""
Live-stream gift flow tests.

Each gift atomically:
- deducts coin_cost from sender's balance
- credits cost - 20% fee (min 1 coin if cost >= 5) to host's withdrawable_balance
- creates a GiftSend, a PlatformEarnings row, and TWO CoinTransaction audit
  rows (sender & recipient)

Bugs in this path = users either lose coins without payout, or the platform
double-credits. Coverage focuses on the rules: auth, ownership, balance,
catalog/stream existence, fee math.
"""
from __future__ import annotations

import pytest

from app.models.coin_transaction import CoinTransaction
from app.models.coin_wallet import CoinWallet
from app.models.gift import GiftCatalog, GiftSend
from app.models.live_stream import LiveStream
from app.models.platform_earnings import PlatformEarnings


GIFT_PATH = "/api/v1/live/{room}/gift"
CATALOG_PATH = "/api/v1/live/gifts/catalog"


@pytest.fixture
def make_gift(db_session):
    """Seed a GiftCatalog row."""
    session, _ = db_session

    def _make(name: str = "Rose", coin_cost: int = 10, emoji: str = "🌹"):
        g = GiftCatalog(
            name=name,
            emoji=emoji,
            coin_cost=coin_cost,
            animation_type="float",
            sort_order=0,
        )
        session.add(g)
        session.commit()
        session.refresh(g)
        return g

    return _make


# ---------- Catalog ----------

def test_catalog_lists_gifts_publicly(client, make_gift):
    make_gift(name="Heart", coin_cost=5)
    make_gift(name="Fire", coin_cost=20)
    resp = client.get(CATALOG_PATH)
    assert resp.status_code == 200
    body = resp.json()
    names = {g["name"] for g in body["gifts"]}
    assert {"Heart", "Fire"} <= names


# ---------- Send: validation ----------

def test_send_gift_requires_auth(client):
    resp = client.post(GIFT_PATH.format(room="any"), json={"gift_id": 1})
    assert resp.status_code == 401


def test_send_gift_missing_id_returns_400(client, make_user, auth_header):
    sender = make_user(email="s@example.com", username="s")
    resp = client.post(
        GIFT_PATH.format(room="any"),
        json={},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 400


def test_send_gift_unknown_gift_returns_404(client, make_user, auth_header):
    sender = make_user(email="s2@example.com", username="s2")
    resp = client.post(
        GIFT_PATH.format(room="any"),
        json={"gift_id": 99999},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 404
    assert "gift" in resp.json()["detail"].lower()


def test_send_gift_unknown_stream_returns_404(client, make_user, make_gift, auth_header):
    sender = make_user(email="s3@example.com", username="s3")
    gift = make_gift()
    resp = client.post(
        GIFT_PATH.format(room="ghost-room"),
        json={"gift_id": gift.id},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 404
    assert "stream" in resp.json()["detail"].lower()


def test_send_gift_to_ended_stream_returns_404(
    client, make_user, make_gift, make_stream, auth_header
):
    host = make_user(email="h1@example.com", username="h1")
    sender = make_user(email="s4@example.com", username="s4")
    gift = make_gift()
    make_stream("dead-room", host_user_id=host.id, status="ended")
    resp = client.post(
        GIFT_PATH.format(room="dead-room"),
        json={"gift_id": gift.id},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 404


def test_host_cannot_gift_themselves(
    client, make_user, make_gift, make_stream, make_wallet, auth_header
):
    host = make_user(email="h2@example.com", username="h2")
    gift = make_gift()
    make_stream("self-room", host_user_id=host.id)
    make_wallet(host.id, balance=10_000)
    resp = client.post(
        GIFT_PATH.format(room="self-room"),
        json={"gift_id": gift.id},
        headers=auth_header(host.id),
    )
    assert resp.status_code == 400
    assert "yourself" in resp.json()["detail"].lower()


def test_send_gift_insufficient_balance_returns_402(
    client, make_user, make_gift, make_stream, make_wallet, auth_header
):
    host = make_user(email="h3@example.com", username="h3")
    sender = make_user(email="s5@example.com", username="s5")
    gift = make_gift(coin_cost=100)
    make_stream("poor-room", host_user_id=host.id)
    make_wallet(sender.id, balance=50)  # less than 100
    resp = client.post(
        GIFT_PATH.format(room="poor-room"),
        json={"gift_id": gift.id},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 402
    assert "insufficient" in resp.json()["detail"].lower()


# ---------- Send: success path ----------

def test_send_gift_atomic_transfer_and_fee_math(
    client, db_session, make_user, make_gift, make_stream, make_wallet, auth_header
):
    """Sender pays cost; host gets cost - fee; platform records the fee.
    All side-effects in a single commit; no partial state on success."""
    session, _ = db_session
    host = make_user(email="h4@example.com", username="h4")
    sender = make_user(email="s6@example.com", username="s6")
    gift = make_gift(name="Diamond", coin_cost=100)  # fee = max(1, 20) = 20

    make_stream("rich-room", host_user_id=host.id)
    make_wallet(sender.id, balance=500)
    make_wallet(host.id, withdrawable_balance=0, lifetime_earned=0)

    resp = client.post(
        GIFT_PATH.format(room="rich-room"),
        json={"gift_id": gift.id},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 200

    session.expire_all()

    sender_wallet = session.query(CoinWallet).filter_by(user_id=sender.id).one()
    assert sender_wallet.balance == 500 - 100
    assert sender_wallet.lifetime_spent == 100

    host_wallet = session.query(CoinWallet).filter_by(user_id=host.id).one()
    assert host_wallet.withdrawable_balance == 80  # 100 - 20% fee
    assert host_wallet.lifetime_earned == 80

    # PlatformEarnings recorded the fee split
    pe = session.query(PlatformEarnings).filter_by(stream_room_name="rich-room").one()
    assert pe.amount == 100
    assert pe.fee_amount == 20
    assert pe.host_amount == 80

    # GiftSend row written
    gs = session.query(GiftSend).filter_by(stream_room_name="rich-room").one()
    assert gs.sender_user_id == sender.id
    assert gs.recipient_user_id == host.id
    assert gs.coin_amount == 100

    # Two ledger rows: sender debit, host credit
    sender_tx = session.query(CoinTransaction).filter_by(user_id=sender.id, type="gift_sent").one()
    assert sender_tx.amount == -100
    host_tx = session.query(CoinTransaction).filter_by(user_id=host.id, type="gift_received").one()
    assert host_tx.amount == 80


def test_small_gift_under_5_coins_has_no_fee(
    client, db_session, make_user, make_gift, make_stream, make_wallet, auth_header
):
    """Fee only applies when coin_cost >= 5."""
    session, _ = db_session
    host = make_user(email="h5@example.com", username="h5")
    sender = make_user(email="s7@example.com", username="s7")
    gift = make_gift(name="Wave", coin_cost=3)
    make_stream("wave-room", host_user_id=host.id)
    make_wallet(sender.id, balance=100)

    resp = client.post(
        GIFT_PATH.format(room="wave-room"),
        json={"gift_id": gift.id},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 200

    session.expire_all()
    host_wallet = session.query(CoinWallet).filter_by(user_id=host.id).one()
    # No fee taken — host gets all 3 coins
    assert host_wallet.withdrawable_balance == 3
    assert host_wallet.lifetime_earned == 3

    pe = session.query(PlatformEarnings).filter_by(stream_room_name="wave-room").one()
    assert pe.fee_amount == 0
    assert pe.host_amount == 3


def test_minimum_fee_is_one_coin(
    client, db_session, make_user, make_gift, make_stream, make_wallet, auth_header
):
    """For a 5-coin gift, 20% = 1.0; with floor + max(1, ...) the fee is 1."""
    session, _ = db_session
    host = make_user(email="h6@example.com", username="h6")
    sender = make_user(email="s8@example.com", username="s8")
    gift = make_gift(name="Spark", coin_cost=5)
    make_stream("spark-room", host_user_id=host.id)
    make_wallet(sender.id, balance=100)

    resp = client.post(
        GIFT_PATH.format(room="spark-room"),
        json={"gift_id": gift.id},
        headers=auth_header(sender.id),
    )
    assert resp.status_code == 200

    session.expire_all()
    host_wallet = session.query(CoinWallet).filter_by(user_id=host.id).one()
    assert host_wallet.withdrawable_balance == 4  # 5 - 1

    pe = session.query(PlatformEarnings).filter_by(stream_room_name="spark-room").one()
    assert pe.fee_amount == 1
    assert pe.host_amount == 4
