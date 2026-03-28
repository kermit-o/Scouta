"""
Coin wallet — balance, purchase via Stripe, transaction history
"""
import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.models.coin_wallet import CoinWallet
from app.models.coin_transaction import CoinTransaction

router = APIRouter(prefix="/coins", tags=["coins"])

# Coin packages: {package_id: (coins, price_cents)}
COIN_PACKAGES = {
    "pack_100": (100, 99),       # 100 coins = $0.99
    "pack_500": (500, 399),      # 500 coins = $3.99
    "pack_2000": (2000, 1499),   # 2000 coins = $14.99
}


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


# ─── GET /coins/balance ──────────────────────────────────────────────────────
@router.get("/balance")
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = _get_or_create_wallet(db, current_user.id)
    return {
        "balance": wallet.balance,
        "lifetime_earned": wallet.lifetime_earned,
        "lifetime_spent": wallet.lifetime_spent,
    }


# ─── GET /coins/packages ─────────────────────────────────────────────────────
@router.get("/packages")
def list_packages():
    return [
        {"id": k, "coins": v[0], "price_cents": v[1]}
        for k, v in COIN_PACKAGES.items()
    ]


# ─── POST /coins/purchase ────────────────────────────────────────────────────
@router.post("/purchase")
def purchase_coins(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe PaymentIntent for a coin package."""
    package_id = body.get("package_id")
    if package_id not in COIN_PACKAGES:
        raise HTTPException(400, f"Invalid package_id. Options: {list(COIN_PACKAGES.keys())}")

    coins, price_cents = COIN_PACKAGES[package_id]
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Ensure Stripe customer exists
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.display_name or current_user.username or current_user.email,
            metadata={"user_id": str(current_user.id)},
        )
        current_user.stripe_customer_id = customer.id
        db.commit()

    # Create PaymentIntent with coin metadata
    intent = stripe.PaymentIntent.create(
        amount=price_cents,
        currency="usd",
        customer=current_user.stripe_customer_id,
        metadata={
            "type": "coin_purchase",
            "user_id": str(current_user.id),
            "coin_amount": str(coins),
            "package_id": package_id,
        },
    )

    return {
        "client_secret": intent.client_secret,
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "coins": coins,
        "price_cents": price_cents,
    }


# ─── GET /coins/transactions ─────────────────────────────────────────────────
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
