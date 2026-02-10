"""
Billing API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

# Import from correct database location
try:
    from core.database.database import SessionLocal, get_db
    from core.database.models import User, Subscription
except ImportError as e:
    logging.warning(f"Database imports failed: {e}")
    SessionLocal = None
    get_db = None
    User = type('User', (), {})
    Subscription = type('Subscription', (), {})

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def handle_billing_webhook(payload: Dict[str, Any]):
    """Handle billing webhooks from payment providers"""
    try:
        logger.info(f"Received billing webhook: {payload}")
        
        # Process webhook based on event type
        event_type = payload.get("type", "")
        
        if event_type == "invoice.payment_succeeded":
            # Handle successful payment
            customer_id = payload.get("data", {}).get("object", {}).get("customer", "")
            logger.info(f"Payment succeeded for customer: {customer_id}")
            
        elif event_type == "invoice.payment_failed":
            # Handle failed payment
            customer_id = payload.get("data", {}).get("object", {}).get("customer", "")
            logger.warning(f"Payment failed for customer: {customer_id}")
            
        return {"status": "processed", "event": event_type}
        
    except Exception as e:
        logger.error(f"Error processing billing webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")

@router.get("/subscriptions/{user_id}")
async def get_user_subscription(user_id: str):
    """Get subscription info for a user"""
    try:
        # Mock implementation for now
        return {
            "user_id": user_id,
            "plan": "premium",
            "status": "active",
            "billing_period": "monthly"
        }
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving subscription")
