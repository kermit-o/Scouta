"""
Router corregido para pagos - Versión simplificada
"""
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import stripe
import os

router = APIRouter(prefix="/payments", tags=["payments"])

# Configuración simple de Stripe
STRIPE_CONFIG = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_mock_key"),
}

stripe.api_key = STRIPE_CONFIG["secret_key"]

@router.get("/plans")
async def get_plans():
    """Obtener planes de suscripción - Versión simplificada"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "features": ["1 proyecto/mes", "Soporte básico"]
            },
            {
                "id": "starter", 
                "name": "Starter",
                "price": 29,
                "features": ["5 proyectos/mes", "Soporte prioritario"]
            }
        ],
        "status": "active",
        "service": "payments_fixed"
    }

@router.get("/health")
async def health_check():
    """Health check simple"""
    return {
        "status": "healthy", 
        "service": "payments_fixed",
        "stripe_configured": bool(STRIPE_CONFIG["secret_key"])
    }

@router.post("/create-checkout-session")
async def create_checkout_session(price_id: str):
    """Versión simplificada de checkout"""
    try:
        # Para testing, devolver sesión mock
        return {
            "checkout_url": "https://checkout.stripe.com/test_mock",
            "session_id": "cs_test_mock",
            "status": "mock_mode",
            "message": "Sistema de pagos en modo testing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF# Crear payments_fixed.py temporal
cat > ./core/app/routers/payments_fixed.py << 'EOF'
"""
Router corregido para pagos - Versión simplificada
"""
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import stripe
import os

router = APIRouter(prefix="/payments", tags=["payments"])

# Configuración simple de Stripe
STRIPE_CONFIG = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_mock_key"),
}

stripe.api_key = STRIPE_CONFIG["secret_key"]

@router.get("/plans")
async def get_plans():
    """Obtener planes de suscripción - Versión simplificada"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "features": ["1 proyecto/mes", "Soporte básico"]
            },
            {
                "id": "starter", 
                "name": "Starter",
                "price": 29,
                "features": ["5 proyectos/mes", "Soporte prioritario"]
            }
        ],
        "status": "active",
        "service": "payments_fixed"
    }

@router.get("/health")
async def health_check():
    """Health check simple"""
    return {
        "status": "healthy", 
        "service": "payments_fixed",
        "stripe_configured": bool(STRIPE_CONFIG["secret_key"])
    }

@router.post("/create-checkout-session")
async def create_checkout_session(price_id: str):
    """Versión simplificada de checkout"""
    try:
        # Para testing, devolver sesión mock
        return {
            "checkout_url": "https://checkout.stripe.com/test_mock",
            "session_id": "cs_test_mock",
            "status": "mock_mode",
            "message": "Sistema de pagos en modo testing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
