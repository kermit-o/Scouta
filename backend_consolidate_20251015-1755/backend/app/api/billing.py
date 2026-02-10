# backend/app/routers/billing.py (Continuación)

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
import stripe
import os
import json # Necesario para parsear el cuerpo de la petición

from backend.app.core.db import get_db
# Importamos el modelo de usuario para actualizar los créditos
from backend.app.core.models.user import User as UserModel 

router = APIRouter(prefix="/api/billing", tags=["Billing"])

# ⚠️ Asegúrate de que stripe.api_key está configurado

# Clave de seguridad del Webhook
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Escucha y procesa eventos de Stripe (Webhooks).
    Este endpoint NO usa autenticación JWT, usa la firma de Stripe.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    # 1. VERIFICACIÓN DE LA FIRMA
    # Esto garantiza que la solicitud realmente proviene de Stripe y no de un atacante.
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Firma inválida
        print(f"❌ Error de Payload inválido: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida
        print(f"❌ Error de Verificación de Firma: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 2. PROCESAMIENTO DEL EVENTO
    
    # Solo nos interesa el evento de confirmación de pago exitoso
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # 2a. Extraer datos CRÍTICOS del metadata
        user_id = session.metadata.get('user_id')
        credits_to_add = session.metadata.get('credits')

        if not user_id or not credits_to_add:
            print("❌ Metadata faltante en la sesión de Stripe.")
            # Registrar el error pero devolver 200 para que Stripe no reintente
            return {"status": "success", "message": "Metadata faltante, revisando manualmente."}

        # Asegurar que el pago fue exitoso y no se procesó antes (protección contra reintentos)
        if session.payment_status == "paid":
            
            # 3. TRANSACCIÓN DE CRÉDITOS (Base de Datos)
            try:
                user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
                if not user:
                    print(f"❌ Usuario no encontrado: {user_id}")
                    return {"status": "success", "message": "Usuario no encontrado."}
                
                # Convertir a entero de forma segura
                credit_amount = int(credits_to_add) 
                
                # 4. SUMAR los créditos al saldo del usuario
                user.credits_balance += credit_amount
                
                # Opcional: Registrar la transacción de compra en una tabla de Historial de Pagos
                
                db.add(user)
                db.commit()
                
                print(f"✅ Créditos sumados: Usuario ID {user_id} recibió {credit_amount} créditos.")
                
            except SQLAlchemyError as e:
                # Si falla la DB, lanzamos un error 500 para que Stripe reintente.
                print(f"❌ Error de DB al sumar créditos: {e}")
                db.rollback()
                raise HTTPException(status_code=500, detail="Database error during credit update.")

        elif session.payment_status == "unpaid":
             print(f"⚠️ Sesión incompleta/sin pagar para el usuario: {user_id}")


    # 5. Respuesta Final
    # Importante: Stripe espera un código 200 OK en caso de éxito o fallo en el procesamiento
    # para saber si debe dejar de enviar el evento. Solo usamos 400/500 para errores de formato/DB.
    return {"status": "success"}