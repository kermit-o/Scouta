"""In-app purchase (IAP) receipt verification — Apple App Store + Google Play.

Store policy (App Store Guideline 3.1.1 and Google Play) requires digital goods
(coins) bought inside a native app to go through platform billing, with the
receipt verified SERVER-SIDE before crediting. Stripe stays web-only.

FAILS CLOSED: if verification can't be performed (missing config) or the receipt
is invalid, NO coins are credited. Idempotent: a transaction id is credited once.

Required env config (set by the team; without it the endpoint returns 503):
  APPLE_IAP_SHARED_SECRET     App-specific shared secret (App Store Connect)
  GOOGLE_PLAY_PACKAGE_NAME    Android applicationId (e.g. co.scouta.app)
  GOOGLE_PLAY_ACCESS_TOKEN    OAuth token for the Play Developer API (mint it
                              from a service account in your infra/cron)

NOTE: untested against live Apple/Google endpoints in this environment — verify
in sandbox before shipping. The SKUs below must match App Store Connect / Play
Console product ids.
"""
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.coin_wallet import CoinWallet
from app.models.coin_transaction import CoinTransaction

router = APIRouter(prefix="/iap", tags=["iap"])

# product_id (SKU in App Store Connect / Play Console) -> coins granted.
IAP_PRODUCTS = {
    "coins_100": 100,
    "coins_500": 500,
    "coins_2000": 2000,
}

APPLE_SHARED_SECRET = os.getenv("APPLE_IAP_SHARED_SECRET", "")
APPLE_VERIFY_PROD = "https://buy.itunes.apple.com/verifyReceipt"
APPLE_VERIFY_SANDBOX = "https://sandbox.itunes.apple.com/verifyReceipt"
GOOGLE_PACKAGE = os.getenv("GOOGLE_PLAY_PACKAGE_NAME", "")
GOOGLE_ACCESS_TOKEN = os.getenv("GOOGLE_PLAY_ACCESS_TOKEN", "")


class VerifyIn(BaseModel):
    platform: str                          # "ios" | "android"
    product_id: str
    transaction_id: str
    receipt: Optional[str] = None          # iOS: base64 receipt-data
    purchase_token: Optional[str] = None   # Android: purchase token


def _get_or_create_wallet(db: Session, user_id: int) -> CoinWallet:
    w = db.query(CoinWallet).filter(CoinWallet.user_id == user_id).first()
    if not w:
        w = CoinWallet(user_id=user_id, balance=0)
        db.add(w)
        db.commit()
        db.refresh(w)
    return w


def _verify_apple(receipt_b64: str, product_id: str, transaction_id: str) -> Optional[bool]:
    """True=valid, False=invalid, None=not configured / unverifiable."""
    if not APPLE_SHARED_SECRET or not receipt_b64:
        return None
    body = {"receipt-data": receipt_b64, "password": APPLE_SHARED_SECRET, "exclude-old-transactions": False}
    try:
        data = httpx.post(APPLE_VERIFY_PROD, json=body, timeout=10).json()
        if data.get("status") == 21007:  # sandbox receipt sent to prod → retry sandbox
            data = httpx.post(APPLE_VERIFY_SANDBOX, json=body, timeout=10).json()
    except Exception:
        return None
    if data.get("status") != 0:
        return False
    # Confirm the receipt actually contains this product + transaction id.
    items = list(data.get("receipt", {}).get("in_app", [])) + list(data.get("latest_receipt_info", []))
    for it in items:
        if it.get("product_id") == product_id and it.get("transaction_id") == transaction_id:
            return True
    return False


def _verify_google(purchase_token: str, product_id: str) -> Optional[bool]:
    """True=valid, False=invalid, None=not configured / unverifiable."""
    if not (GOOGLE_PACKAGE and GOOGLE_ACCESS_TOKEN and purchase_token):
        return None
    url = (
        "https://androidpublisher.googleapis.com/androidpublisher/v3/applications/"
        f"{GOOGLE_PACKAGE}/purchases/products/{product_id}/tokens/{purchase_token}"
    )
    try:
        r = httpx.get(url, headers={"Authorization": f"Bearer {GOOGLE_ACCESS_TOKEN}"}, timeout=10)
    except Exception:
        return None
    if r.status_code != 200:
        return False
    # purchaseState: 0 = purchased, 1 = canceled, 2 = pending.
    return r.json().get("purchaseState", 1) == 0


@router.post("/verify")
def verify_purchase(
    payload: VerifyIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    platform = (payload.platform or "").lower()
    coins = IAP_PRODUCTS.get(payload.product_id)
    if coins is None:
        raise HTTPException(status_code=400, detail="unknown product_id")
    if not payload.transaction_id:
        raise HTTPException(status_code=400, detail="transaction_id required")

    # Idempotency: a given store transaction credits coins exactly once.
    ref = f"iap_{platform}_{payload.transaction_id}"
    already = (
        db.query(CoinTransaction)
        .filter(CoinTransaction.reference_id == ref, CoinTransaction.type == "purchase")
        .first()
    )
    if already:
        return {"status": "already_credited"}

    if platform == "ios":
        ok = _verify_apple(payload.receipt or "", payload.product_id, payload.transaction_id)
    elif platform == "android":
        ok = _verify_google(payload.purchase_token or "", payload.product_id)
    else:
        raise HTTPException(status_code=400, detail="platform must be 'ios' or 'android'")

    if ok is None:
        raise HTTPException(status_code=503, detail="IAP verification not configured for this platform")
    if not ok:
        raise HTTPException(status_code=400, detail="receipt verification failed")

    wallet = _get_or_create_wallet(db, user.id)
    wallet.balance += coins
    db.add(CoinTransaction(
        user_id=user.id,
        amount=coins,
        type="purchase",
        reference_id=ref,
        description=f"IAP {payload.product_id} (+{coins} coins)",
    ))
    db.commit()
    return {"status": "credited", "coins": coins, "balance": wallet.balance}


@router.get("/products")
def list_iap_products():
    """SKUs the clients should offer (must match the store consoles)."""
    return [{"product_id": k, "coins": v} for k, v in IAP_PRODUCTS.items()]
