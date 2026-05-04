"""
Withdrawal flow tests.

These hit the /coins/withdraw endpoint plus the admin approve/reject endpoints.
This is the path where real money leaves the platform — bugs here = lost
money, so coverage focuses on the rules: minimum amount, valid methods,
sufficient withdrawable balance, no double-pending, exact admin transitions.
"""
from __future__ import annotations

from app.models.coin_transaction import CoinTransaction
from app.models.coin_wallet import CoinWallet
from app.models.withdrawal_request import WithdrawalRequest


WITHDRAW_PATH = "/api/v1/coins/withdraw"
LIST_PATH = "/api/v1/coins/withdrawals"
ADMIN_LIST_PATH = "/api/v1/coins/admin/withdrawals"
ADMIN_APPROVE_PATH = "/api/v1/coins/admin/withdrawals/{id}/approve"
ADMIN_REJECT_PATH = "/api/v1/coins/admin/withdrawals/{id}/reject"


def _ok_payload(amount=600, method="paypal", details="user@paypal.com"):
    return {"amount_coins": amount, "method": method, "payout_details": details}


# ---------- Create withdrawal ----------

def test_withdraw_requires_auth(client):
    resp = client.post(WITHDRAW_PATH, json=_ok_payload())
    assert resp.status_code == 401


def test_withdraw_below_minimum_returns_400(client, make_user, make_wallet, auth_header):
    user = make_user(email="low@example.com", username="low")
    make_wallet(user.id, balance=0, withdrawable_balance=10_000)
    resp = client.post(
        WITHDRAW_PATH,
        json=_ok_payload(amount=100),  # MIN_WITHDRAWAL_COINS is 500
        headers=auth_header(user.id),
    )
    assert resp.status_code == 400
    assert "minimum" in resp.json()["detail"].lower()


def test_withdraw_invalid_method_returns_400(client, make_user, make_wallet, auth_header):
    user = make_user(email="badmethod@example.com", username="badmethod")
    make_wallet(user.id, withdrawable_balance=10_000)
    resp = client.post(
        WITHDRAW_PATH,
        json=_ok_payload(method="bitcoin"),
        headers=auth_header(user.id),
    )
    assert resp.status_code == 400
    assert "method" in resp.json()["detail"].lower()


def test_withdraw_missing_payout_details_returns_400(client, make_user, make_wallet, auth_header):
    user = make_user(email="nodet@example.com", username="nodet")
    make_wallet(user.id, withdrawable_balance=10_000)
    resp = client.post(
        WITHDRAW_PATH,
        json=_ok_payload(details=""),
        headers=auth_header(user.id),
    )
    assert resp.status_code == 400
    assert "payout details" in resp.json()["detail"].lower()


def test_withdraw_insufficient_balance_returns_400(client, make_user, make_wallet, auth_header):
    user = make_user(email="poor@example.com", username="poor")
    make_wallet(user.id, withdrawable_balance=400)  # below the 600 they ask for
    resp = client.post(WITHDRAW_PATH, json=_ok_payload(), headers=auth_header(user.id))
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


def test_withdraw_success_deducts_and_creates_pending_request(
    client, db_session, make_user, make_wallet, auth_header
):
    session, _ = db_session
    user = make_user(email="ok@example.com", username="okuser")
    make_wallet(user.id, withdrawable_balance=2_000)

    resp = client.post(WITHDRAW_PATH, json=_ok_payload(amount=800), headers=auth_header(user.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["status"] == "pending"
    assert body["amount_coins"] == 800

    session.expire_all()
    wallet = session.query(CoinWallet).filter_by(user_id=user.id).one()
    assert wallet.withdrawable_balance == 2_000 - 800

    wr = session.query(WithdrawalRequest).filter_by(user_id=user.id).one()
    assert wr.status == "pending"
    assert wr.amount_coins == 800
    assert wr.payout_method == "paypal"
    assert wr.payout_details == "user@paypal.com"

    # Audit trail logged
    tx = session.query(CoinTransaction).filter_by(user_id=user.id, type="withdrawal").one()
    assert tx.amount == -800


def test_withdraw_blocks_second_pending_request(
    client, db_session, make_user, make_wallet, auth_header
):
    session, _ = db_session
    user = make_user(email="dup@example.com", username="dupuser")
    make_wallet(user.id, withdrawable_balance=10_000)

    r1 = client.post(WITHDRAW_PATH, json=_ok_payload(amount=600), headers=auth_header(user.id))
    assert r1.status_code == 200

    r2 = client.post(WITHDRAW_PATH, json=_ok_payload(amount=700), headers=auth_header(user.id))
    assert r2.status_code == 400
    assert "pending" in r2.json()["detail"].lower()

    session.expire_all()
    wallet = session.query(CoinWallet).filter_by(user_id=user.id).one()
    # Only the first deduction took effect.
    assert wallet.withdrawable_balance == 10_000 - 600


# ---------- User listing ----------

def test_list_withdrawals_returns_only_owners_rows(
    client, db_session, make_user, make_wallet, auth_header
):
    session, _ = db_session
    alice = make_user(email="alice@example.com", username="alice")
    bob = make_user(email="bob@example.com", username="bob")
    make_wallet(alice.id, withdrawable_balance=10_000)
    make_wallet(bob.id, withdrawable_balance=10_000)

    client.post(WITHDRAW_PATH, json=_ok_payload(amount=600, details="alice@paypal"), headers=auth_header(alice.id))
    client.post(WITHDRAW_PATH, json=_ok_payload(amount=700, details="bob@paypal"), headers=auth_header(bob.id))

    resp = client.get(LIST_PATH, headers=auth_header(alice.id))
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["amount_coins"] == 600
    assert rows[0]["method"] == "paypal"


# ---------- Admin approve ----------

def test_admin_approve_requires_superuser(
    client, make_user, make_wallet, auth_header
):
    plain_user = make_user(email="plain@example.com", username="plain")
    make_wallet(plain_user.id, withdrawable_balance=10_000)
    r = client.post(WITHDRAW_PATH, json=_ok_payload(), headers=auth_header(plain_user.id))
    wr_id = r.json()["id"]

    # Same plain user trying to approve their own withdrawal — must be blocked.
    resp = client.post(ADMIN_APPROVE_PATH.format(id=wr_id), headers=auth_header(plain_user.id))
    assert resp.status_code in (401, 403)


def test_admin_approve_marks_completed(
    client, db_session, make_user, make_wallet, auth_header
):
    session, _ = db_session
    user = make_user(email="seller@example.com", username="seller")
    admin = make_user(email="admin@example.com", username="admin", is_superuser=True)
    make_wallet(user.id, withdrawable_balance=10_000)
    r = client.post(WITHDRAW_PATH, json=_ok_payload(amount=800), headers=auth_header(user.id))
    wr_id = r.json()["id"]

    resp = client.post(
        ADMIN_APPROVE_PATH.format(id=wr_id),
        json={"reference": "PAYPAL-TX-12345"},
        headers=auth_header(admin.id),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["external_reference"] == "PAYPAL-TX-12345"
    assert body["completed_at"]

    session.expire_all()
    wr = session.get(WithdrawalRequest, wr_id)
    assert wr.status == "completed"
    assert wr.completed_at is not None
    # The user's withdrawable was deducted on creation; approval doesn't double-deduct.
    wallet = session.query(CoinWallet).filter_by(user_id=user.id).one()
    assert wallet.withdrawable_balance == 10_000 - 800


def test_admin_approve_already_completed_returns_400(
    client, make_user, make_wallet, auth_header
):
    user = make_user(email="seller2@example.com", username="seller2")
    admin = make_user(email="admin2@example.com", username="admin2", is_superuser=True)
    make_wallet(user.id, withdrawable_balance=10_000)
    r = client.post(WITHDRAW_PATH, json=_ok_payload(), headers=auth_header(user.id))
    wr_id = r.json()["id"]

    # First approval
    r1 = client.post(ADMIN_APPROVE_PATH.format(id=wr_id), headers=auth_header(admin.id))
    assert r1.status_code == 200

    # Second approval — must reject because status is now 'completed', not 'pending'
    r2 = client.post(ADMIN_APPROVE_PATH.format(id=wr_id), headers=auth_header(admin.id))
    assert r2.status_code == 400
    assert "completed" in r2.json()["detail"].lower()


def test_admin_approve_404_on_missing(client, make_user, auth_header):
    admin = make_user(email="admin3@example.com", username="admin3", is_superuser=True)
    resp = client.post(ADMIN_APPROVE_PATH.format(id=99999), headers=auth_header(admin.id))
    assert resp.status_code == 404


# ---------- Admin reject ----------

def test_admin_reject_requires_reason(
    client, make_user, make_wallet, auth_header
):
    user = make_user(email="seller3@example.com", username="seller3")
    admin = make_user(email="admin4@example.com", username="admin4", is_superuser=True)
    make_wallet(user.id, withdrawable_balance=10_000)
    r = client.post(WITHDRAW_PATH, json=_ok_payload(), headers=auth_header(user.id))
    wr_id = r.json()["id"]

    resp = client.post(
        ADMIN_REJECT_PATH.format(id=wr_id),
        json={"reason": ""},
        headers=auth_header(admin.id),
    )
    assert resp.status_code == 400
    assert "reason" in resp.json()["detail"].lower()


def test_admin_reject_refunds_withdrawable_balance(
    client, db_session, make_user, make_wallet, auth_header
):
    session, _ = db_session
    user = make_user(email="seller4@example.com", username="seller4")
    admin = make_user(email="admin5@example.com", username="admin5", is_superuser=True)
    make_wallet(user.id, withdrawable_balance=10_000)
    r = client.post(WITHDRAW_PATH, json=_ok_payload(amount=900), headers=auth_header(user.id))
    wr_id = r.json()["id"]

    # After creation, balance dropped by 900
    session.expire_all()
    assert session.query(CoinWallet).filter_by(user_id=user.id).one().withdrawable_balance == 10_000 - 900

    resp = client.post(
        ADMIN_REJECT_PATH.format(id=wr_id),
        json={"reason": "Invalid PayPal account"},
        headers=auth_header(admin.id),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "failed"
    assert body["refunded_coins"] == 900

    session.expire_all()
    # Refund: balance is back to original 10_000
    assert session.query(CoinWallet).filter_by(user_id=user.id).one().withdrawable_balance == 10_000

    wr = session.get(WithdrawalRequest, wr_id)
    assert wr.status == "failed"
    assert "Invalid PayPal" in wr.failure_reason

    # An audit refund row was logged
    refund = session.query(CoinTransaction).filter_by(user_id=user.id, type="refund").one()
    assert refund.amount == 900


def test_admin_reject_already_rejected_returns_400(
    client, make_user, make_wallet, auth_header
):
    user = make_user(email="seller5@example.com", username="seller5")
    admin = make_user(email="admin6@example.com", username="admin6", is_superuser=True)
    make_wallet(user.id, withdrawable_balance=10_000)
    r = client.post(WITHDRAW_PATH, json=_ok_payload(), headers=auth_header(user.id))
    wr_id = r.json()["id"]

    r1 = client.post(
        ADMIN_REJECT_PATH.format(id=wr_id),
        json={"reason": "first reject"},
        headers=auth_header(admin.id),
    )
    assert r1.status_code == 200

    r2 = client.post(
        ADMIN_REJECT_PATH.format(id=wr_id),
        json={"reason": "second reject"},
        headers=auth_header(admin.id),
    )
    assert r2.status_code == 400
