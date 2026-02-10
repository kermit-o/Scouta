"""
Router para manejar pagos y suscripciones con Stripe - Integrado con auth JWT
"""
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

from app.core.database.subscription_db import get_db
from backend.app.core.database.models import User

# Importar el sistema de auth real
from backend.app.auth import AuthManager

router = APIRouter(prefix="/payments", tags=["payments"])

# Configuración de Stripe desde variables de entorno
STRIPE_CONFIG = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY", "sk_test_missing_key"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_missing_key"),
    "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_missing_secret"),
    "prices": {
        "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter_mock"),
        "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_mock"), 
        "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise_mock")
    }
}

# Configurar Stripe
stripe.api_key = STRIPE_CONFIG["secret_key"]

@router.get("/plans")
async def get_plans():
    """Obtener planes de suscripción disponibles"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "features": [
                    "1 proyecto por mes",
                    "10 peticiones IA por mes",
                    "Soporte básico"
                ],
                "limits": {
                    "projects": 1,
                    "ai_requests": 10
                }
            },
            {
                "id": "starter",
                "name": "Starter",
                "price": 29,
                "features": [
                    "5 proyectos por mes",
                    "100 peticiones IA por mes", 
                    "Soporte prioritario",
                    "Todos los generadores"
                ],
                "limits": {
                    "projects": 5,
                    "ai_requests": 100
                },
                "price_id": STRIPE_CONFIG["prices"]["starter"]
            },
            {
                "id": "pro", 
                "name": "Pro",
                "price": 79,
                "features": [
                    "50 proyectos por mes",
                    "1000 peticiones IA por mes",
                    "Soporte 24/7",
                    "Deployment automático"
                ],
                "limits": {
                    "projects": 50,
                    "ai_requests": 1000
                },
                "price_id": STRIPE_CONFIG["prices"]["pro"]
            },
            {
                "id": "enterprise",
                "name": "Enterprise", 
                "price": 199,
                "features": [
                    "Proyectos ilimitados",
                    "Peticiones IA ilimitadas",
                    "SLA garantizado",
                    "Cuenta dedicada"
                ],
                "limits": {
                    "projects": 9999,
                    "ai_requests": 99999
                },
                "price_id": STRIPE_CONFIG["prices"]["enterprise"]
            }
        ]
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    success_url: str = "http://localhost:3000/success",
    cancel_url: str = "http://localhost:3000/cancel",
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Crear sesión de checkout de Stripe para usuario autenticado"""
    try:
        # Verificar que el price_id sea válido
        valid_prices = list(STRIPE_CONFIG["prices"].values())
        if price_id not in valid_prices:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid price ID"
            )
        
        # Crear sesión de checkout con datos del usuario real
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=current_user.email,
            metadata={
                'user_id': str(current_user.id),
                'user_email': current_user.email,
                'user_plan': current_user.plan
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "status": "success",
            "user_email": current_user.email,
            "user_plan": current_user.plan
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Manejar webhooks de Stripe"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_CONFIG["webhook_secret"]
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid payload"})
    except stripe.error.SignatureVerificationError:
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})
    
    # Manejar eventos
    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_email = session['metadata']['user_email']
            user_id = session['metadata']['user_id']
            print(f"✅ Checkout completed for user: {user_email} (ID: {user_id})")
            
            # Aquí podrías actualizar la suscripción del usuario en la base de datos
            # basándote en el price_id de la suscripción
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            print(f"📅 Subscription updated: {subscription['id']}")
            
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            print(f"💰 Payment succeeded: {invoice['id']}")
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
    
    return JSONResponse(status_code=200, content={"received": True})

@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener suscripción actual del usuario autenticado"""
    # Por ahora devolver datos basados en el usuario real
    # En implementación real, consultaríamos user_subscriptions
    
    return {
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "current_plan": current_user.plan,
        "status": "active",
        "limits": {
            "projects": current_user.max_projects_per_month,
            "ai_requests": 10  # Podrías agregar este campo al modelo User
        },
        "usage": {
            "projects_used": current_user.projects_used_this_month,
            "ai_requests_used": 0
        },
        "billing_period": {
            "start": "2024-01-01T00:00:00Z",  # Esto vendría de la suscripción real
            "end": "2024-02-01T00:00:00Z"
        },
        "can_create_project": current_user.projects_used_this_month < current_user.max_projects_per_month,
        "remaining_projects": max(0, current_user.max_projects_per_month - current_user.projects_used_this_month)
    }

@router.get("/health")
async def health_check():
    """Health check para el sistema de pagos"""
    return {
        "status": "healthy",
        "service": "payments",
        "stripe_configured": bool(STRIPE_CONFIG["secret_key"] and "missing" not in STRIPE_CONFIG["secret_key"]),
        "auth_system": "jwt",
        "database": "sqlite",
        "version": "1.0"
    }

@router.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Probar conexión a la base de datos"""
    from sqlalchemy import text
    try:
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        return {
            "status": "connected",
            "tables": tables,
            "table_count": len(tables),
            "subscription_tables": [t for t in tables if 'subscription' in t or 'billing' in t]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/my-usage")
async def get_my_usage(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener uso actual del usuario autenticado"""
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "current_plan": current_user.plan,
        "usage": {
            "projects_used": current_user.projects_used_this_month,
            "projects_limit": current_user.max_projects_per_month,
            "remaining_projects": max(0, current_user.max_projects_per_month - current_user.projects_used_this_month)
        },
        "can_create_more_projects": current_user.projects_used_this_month < current_user.max_projects_per_month
    }
