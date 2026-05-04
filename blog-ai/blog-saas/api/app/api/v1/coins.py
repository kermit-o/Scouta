"""
Coin wallet — balance, purchase via Stripe Checkout, transaction history, withdrawals
"""
import json
import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.config import settings
from app.core.deps import get_current_user, require_superuser
from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.models.user import User
from app.models.coin_wallet import CoinWallet
from app.models.coin_transaction import CoinTransaction

log = get_logger(__name__)
router = APIRouter(prefix="/coins", tags=["coins"])

COIN_PACKAGES = {
    "pack_100": (100, 99),
    "pack_500": (500, 399),
    "pack_2000": (2000, 1499),
}

MIN_WITHDRAWAL_COINS = 500
ALLOWED_PAYOUT_METHODS = {"paypal", "bank"}

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://scouta.co").rstrip("/")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_create_wallet(db: Session, user_id: int) -> CoinWallet:
    wallet = db.query(CoinWallet).filter(CoinWallet.user_id == user_id).first()
    if not wallet:
        wallet = CoinWallet(user_id=user_id, balance=0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


@router.get("/balance")
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = _get_or_create_wallet(db, current_user.id)
    return {
        "balance": wallet.balance,
        "withdrawable_balance": wallet.withdrawable_balance,
        "lifetime_earned": wallet.lifetime_earned,
        "lifetime_spent": wallet.lifetime_spent,
    }


@router.get("/packages")
def list_packages():
    return [
        {"id": k, "coins": v[0], "price_cents": v[1]}
        for k, v in COIN_PACKAGES.items()
    ]


@router.post("/purchase")
@limiter.limit("5/minute")
def purchase_coins(
    body: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout Session for a coin package.
    Returns { checkout_url } — frontend redirects to it. Coins are credited
    asynchronously via the /stripe-webhook handler when payment completes.

    NOTE: We use customer_email (not customer=stripe_customer_id) on purpose.
    The User.stripe_customer_id column is shared with Stripe Connect Account IDs
    in /connect-account, so reusing it here would crash for hosts who onboarded
    payouts before purchasing. Stripe will dedupe customers by email server-side.
    """
    package_id = body.get("package_id")
    if package_id not in COIN_PACKAGES:
        raise HTTPException(400, f"Invalid package_id. Options: {list(COIN_PACKAGES.keys())}")

    coins, price_cents = COIN_PACKAGES[package_id]
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=current_user.email,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{coins} Scouta coins",
                        "description": "Use coins to send gifts and unlock paid lives.",
                    },
                    "unit_amount": price_cents,
                },
                "quantity": 1,
            }],
            metadata={
                "type": "coin_purchase",
                "user_id": str(current_user.id),
                "coin_amount": str(coins),
                "package_id": package_id,
            },
            payment_intent_data={
                "metadata": {
                    "type": "coin_purchase",
                    "user_id": str(current_user.id),
                    "coin_amount": str(coins),
                    "package_id": package_id,
                },
            },
            success_url=f"{FRONTEND_URL}/wallet?purchase=success&coins={coins}",
            cancel_url=f"{FRONTEND_URL}/wallet/buy?cancelled=1",
        )
    except stripe.error.StripeError as e:
        raise HTTPException(502, f"Stripe error: {e.user_message or str(e)}")

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "coins": coins,
        "price_cents": price_cents,
    }


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """Stripe webhook endpoint. Receives checkout.session.completed events and
    credits coins to the user's wallet."""
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(500, "Webhook secret not configured (STRIPE_WEBHOOK_SECRET)")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        log.warning("stripe_webhook_invalid_payload")
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        log.warning("stripe_webhook_invalid_signature")
        raise HTTPException(400, "Invalid signature")

    event = json.loads(payload)
    event_id = event.get("id")
    event_type = event.get("type")

    if event_type != "checkout.session.completed":
        log.info("stripe_webhook_ignored", event_id=event_id, event_type=event_type, reason="not_checkout")
        return {"received": True, "ignored": True}

    session = (event.get("data") or {}).get("object") or {}
    metadata = session.get("metadata") or {}
    if metadata.get("type") != "coin_purchase":
        log.info("stripe_webhook_ignored", event_id=event_id, reason="not_coin_purchase", metadata_type=metadata.get("type"))
        return {"received": True, "ignored": True}

    user_id_str = metadata.get("user_id")
    coin_amount_str = metadata.get("coin_amount")
    if not user_id_str or not coin_amount_str:
        log.warning("stripe_webhook_ignored", event_id=event_id, reason="missing_metadata")
        return {"received": True, "ignored": True, "reason": "missing metadata"}

    try:
        user_id = int(user_id_str)
        coin_amount = int(coin_amount_str)
    except ValueError:
        log.warning("stripe_webhook_ignored", event_id=event_id, reason="bad_metadata", user_id=user_id_str, coin_amount=coin_amount_str)
        return {"received": True, "ignored": True, "reason": "bad metadata"}

    session_id = session.get("id") or ""

    # Transaction-scoped advisory lock keyed by the Stripe session id.
    # Postgres-only; SQLite (used in tests) doesn't support pg_advisory_xact_lock.
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(
            sql_text("SELECT pg_advisory_xact_lock(hashtext(:k))"),
            {"k": session_id},
        )

    existing = db.query(CoinTransaction).filter(
        CoinTransaction.reference_id == session_id,
        CoinTransaction.type == "purchase",
    ).first()
    if existing:
        log.info("stripe_webhook_replay", event_id=event_id, session_id=session_id, user_id=user_id)
        return {"received": True, "already_credited": True}

    user = db.get(User, user_id)
    if not user:
        log.warning("stripe_webhook_unknown_user", event_id=event_id, session_id=session_id, user_id=user_id)
        return {"received": True, "ignored": True, "reason": "user not found"}

    wallet = _get_or_create_wallet(db, user_id)
    wallet.balance += coin_amount

    amount_cents = session.get("amount_total") or 0
    db.add(CoinTransaction(
        user_id=user_id,
        amount=coin_amount,
        type="purchase",
        description=f"Purchased {coin_amount} coins (${amount_cents / 100:.2f})",
        reference_id=session_id,
    ))
    db.commit()

    log.info(
        "stripe_webhook_credited",
        event_id=event_id,
        session_id=session_id,
        user_id=user_id,
        coins=coin_amount,
        amount_cents=amount_cents,
    )

    return {
        "received": True,
        "credited": True,
        "user_id": user_id,
        "coins": coin_amount,
    }


@router.get("/transactions")
def list_transactions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txns = (
        db.query(CoinTransaction)
        .filter(CoinTransaction.user_id == current_user.id)
        .order_by(CoinTransaction.created_at.desc())
        .offset(offset)
        .limit(min(limit, 100))
        .all()
    )
    return [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "description": t.description,
            "reference_id": t.reference_id,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in txns
    ]


@router.get("/earnings")
def get_earnings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Host sees total earned, withdrawable, withdrawn, pending."""
    wallet = _get_or_create_wallet(db, current_user.id)

    from app.models.withdrawal_request import WithdrawalRequest
    from sqlalchemy import func as sqlfunc

    withdrawn = db.query(sqlfunc.coalesce(sqlfunc.sum(WithdrawalRequest.amount_coins), 0)).filter(
        WithdrawalRequest.user_id == current_user.id,
        WithdrawalRequest.status == "completed",
    ).scalar()

    pending = db.query(sqlfunc.coalesce(sqlfunc.sum(WithdrawalRequest.amount_coins), 0)).filter(
        WithdrawalRequest.user_id == current_user.id,
        WithdrawalRequest.status.in_(["pending", "processing"]),
    ).scalar()

    return {
        "total_earned": wallet.lifetime_earned,
        "withdrawable": wallet.withdrawable_balance,
        "withdrawn": withdrawn,
        "pending": pending,
    }


@router.post("/withdraw")
@limiter.limit("3/minute")
def request_withdrawal(
    body: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a withdrawal request for manual processing (5–7 business days)."""
    amount_coins = int(body.get("amount") or body.get("amount_coins") or 0)
    method = (body.get("method") or "").strip().lower()
    payout_details = (body.get("payout_details") or "").strip()

    if amount_coins < MIN_WITHDRAWAL_COINS:
        raise HTTPException(400, f"Minimum withdrawal is {MIN_WITHDRAWAL_COINS} coins")
    if method not in ALLOWED_PAYOUT_METHODS:
        raise HTTPException(400, f"Invalid method. Options: {sorted(ALLOWED_PAYOUT_METHODS)}")
    if not payout_details:
        raise HTTPException(400, "Payout details required (PayPal email or bank account details)")

    wallet = _get_or_create_wallet(db, current_user.id)
    if wallet.withdrawable_balance < amount_coins:
        raise HTTPException(400, "Insufficient withdrawable balance")

    from app.models.withdrawal_request import WithdrawalRequest

    pending = db.query(WithdrawalRequest).filter(
        WithdrawalRequest.user_id == current_user.id,
        WithdrawalRequest.status.in_(["pending", "processing"]),
    ).first()
    if pending:
        raise HTTPException(400, "You already have a pending withdrawal")

    amount_cents = int(amount_coins * 0.99)
    wallet.withdrawable_balance -= amount_coins

    withdrawal = WithdrawalRequest(
        user_id=current_user.id,
        amount_coins=amount_coins,
        amount_cents=amount_cents,
        status="pending",
        payout_method=method,
        payout_details=payout_details,
    )
    db.add(withdrawal)

    db.add(CoinTransaction(
        user_id=current_user.id,
        amount=-amount_coins,
        type="withdrawal",
        description=f"Withdrawal requested ({method}, {amount_coins} coins ≈ ${amount_cents / 100:.2f})",
    ))
    db.commit()
    db.refresh(withdrawal)

    return {
        "ok": True,
        "id": withdrawal.id,
        "status": "pending",
        "amount_coins": amount_coins,
        "amount_usd": f"${amount_cents / 100:.2f}",
        "method": method,
        "processing_days": "5-7",
    }


@router.get("/withdrawals")
def list_withdrawals(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.withdrawal_request import WithdrawalRequest
    rows = (
        db.query(WithdrawalRequest)
        .filter(WithdrawalRequest.user_id == current_user.id)
        .order_by(WithdrawalRequest.created_at.desc())
        .offset(offset).limit(min(limit, 50)).all()
    )
    return [
        {
            "id": r.id,
            "amount_coins": r.amount_coins,
            "amount_cents": r.amount_cents,
            "status": r.status,
            "method": r.payout_method,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in rows
    ]


@router.get("/admin/withdrawals")
def admin_list_withdrawals(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):
    """List all withdrawal requests (optionally filtered by status), with user info hydrated."""
    from app.models.withdrawal_request import WithdrawalRequest

    q = db.query(WithdrawalRequest).order_by(WithdrawalRequest.created_at.desc())
    if status:
        q = q.filter(WithdrawalRequest.status == status)
    rows = q.offset(offset).limit(min(limit, 200)).all()

    user_ids = {r.user_id for r in rows}
    users = (
        {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}
        if user_ids
        else {}
    )

    def user_info(uid: int):
        u = users.get(uid)
        if not u:
            return {"id": uid, "username": None, "email": None, "display_name": None}
        return {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "display_name": u.display_name,
        }

    return [
        {
            "id": r.id,
            "user": user_info(r.user_id),
            "amount_coins": r.amount_coins,
            "amount_cents": r.amount_cents,
            "amount_usd": f"${r.amount_cents / 100:.2f}",
            "status": r.status,
            "method": r.payout_method,
            "payout_details": r.payout_details,
            "failure_reason": r.failure_reason,
            "external_reference": r.stripe_transfer_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in rows
    ]


@router.post("/admin/withdrawals/{withdrawal_id}/approve")
def admin_approve_withdrawal(
    withdrawal_id: int,
    body: dict | None = None,
    _: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):
    from app.models.withdrawal_request import WithdrawalRequest
    from datetime import datetime, timezone

    w = db.get(WithdrawalRequest, withdrawal_id)
    if not w:
        raise HTTPException(404, "Withdrawal not found")
    if w.status != "pending":
        raise HTTPException(400, f"Cannot approve withdrawal in status '{w.status}'")

    reference = (body or {}).get("reference") if body else None

    w.status = "completed"
    w.completed_at = datetime.now(timezone.utc)
    if reference:
        w.stripe_transfer_id = str(reference)[:200]
    db.commit()

    return {
        "ok": True,
        "id": w.id,
        "status": w.status,
        "completed_at": w.completed_at.isoformat(),
        "external_reference": w.stripe_transfer_id,
    }


@router.post("/admin/withdrawals/{withdrawal_id}/reject")
def admin_reject_withdrawal(
    withdrawal_id: int,
    body: dict,
    _: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):
    from app.models.withdrawal_request import WithdrawalRequest

    w = db.get(WithdrawalRequest, withdrawal_id)
    if not w:
        raise HTTPException(404, "Withdrawal not found")
    if w.status != "pending":
        raise HTTPException(400, f"Cannot reject withdrawal in status '{w.status}'")

    reason = (body.get("reason") or "").strip()
    if not reason:
        raise HTTPException(400, "Rejection reason required")

    wallet = _get_or_create_wallet(db, w.user_id)
    wallet.withdrawable_balance += w.amount_coins

    w.status = "failed"
    w.failure_reason = reason[:1000]

    db.add(CoinTransaction(
        user_id=w.user_id,
        amount=w.amount_coins,
        type="refund",
        description=f"Withdrawal rejected: {reason[:200]}",
    ))
    db.commit()

    return {
        "ok": True,
        "id": w.id,
        "status": w.status,
        "refunded_coins": w.amount_coins,
    }


@router.post("/connect-account")
def create_connect_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create Stripe Connect Express account for host payouts."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if current_user.stripe_customer_id:
        try:
            acct = stripe.Account.retrieve(current_user.stripe_customer_id)
            if acct["type"] == "express":
                return {"ok": True, "account_id": current_user.stripe_customer_id, "already_exists": True}
        except (KeyError, AttributeError, Exception):
            pass

    account = stripe.Account.create(
        type="express",
        email=current_user.email,
        metadata={"user_id": str(current_user.id)},
        capabilities={"transfers": {"requested": True}},
    )
    current_user.stripe_customer_id = account.id
    db.commit()

    return {"ok": True, "account_id": account.id}


@router.get("/connect-link")
def get_connect_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get Stripe Connect onboarding link for host to set up bank account."""
    if not current_user.stripe_customer_id:
        raise HTTPException(400, "Create a Connect account first")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    link = stripe.AccountLink.create(
        account=current_user.stripe_customer_id,
        refresh_url=f"{FRONTEND_URL}/profile",
        return_url=f"{FRONTEND_URL}/profile?stripe_connected=1",
        type="account_onboarding",
    )
    return {"url": link.url}


@router.get("/connect-status")
def get_connect_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if host has completed Stripe Connect onboarding."""
    if not current_user.stripe_customer_id:
        return {"connected": False, "account_id": None}

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        acct = stripe.Account.retrieve(current_user.stripe_customer_id)
        return {
            "connected": acct.charges_enabled and acct.payouts_enabled,
            "account_id": current_user.stripe_customer_id,
            "charges_enabled": acct.charges_enabled,
            "payouts_enabled": acct.payouts_enabled,
        }
    except Exception:
        return {"connected": False, "account_id": current_user.stripe_customer_id}
