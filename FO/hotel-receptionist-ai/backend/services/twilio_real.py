"""
Servicio real para integración con Twilio
"""
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TwilioRealService:
    """Servicio real para manejar operaciones con Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token]):
            logger.warning("⚠️ Twilio credentials not configured")
            logger.warning("   Get free credits at: https://www.twilio.com/try-twilio")
            self.client = None
            self.is_configured = False
        else:
            self.client = Client(self.account_sid, self.auth_token)
            self.is_configured = True
            logger.info("✅ Twilio service initialized successfully")
    
    def get_phone_numbers(self) -> list:
        """Obtener números telefónicos disponibles en la cuenta"""
        if not self.client:
            return []
        
        try:
            numbers = self.client.incoming_phone_numbers.list(limit=20)
            return [
                {
                    "phone_number": num.phone_number,
                    "friendly_name": num.friendly_name,
                    "sid": num.sid
                }
                for num in numbers
            ]
        except Exception as e:
            logger.error(f"Error fetching phone numbers: {e}")
            return []
    
    def purchase_phone_number(self, area_code: str = "34") -> Optional[Dict]:
        """Comprar un número telefónico (solo funciona en producción con cuenta verificada)"""
        if not self.client:
            return None
        
        try:
            # Para pruebas, usamos números de prueba
            # En producción: new_number = self.client.incoming_phone_numbers.create(area_code=area_code)
            
            return {
                "success": True,
                "message": "En modo desarrollo. En producción puedes comprar números reales.",
                "test_numbers": [
                    "+15005550001",  # Magic Phone Number - siempre funciona
                    "+15005550006",  # Número de prueba
                    "+15005550009"   # Otro número de prueba
                ]
            }
        except Exception as e:
            logger.error(f"Error purchasing phone number: {e}")
            return None
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        """Enviar SMS a un número"""
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            # Para desarrollo, simular envío
            if os.getenv("ENVIRONMENT") == "development":
                logger.info(f"📱 [DEV] SMS would send to {to_number}: {message[:50]}...")
                return {
                    "success": True,
                    "sid": "dev_sms_" + to_number[-8:],
                    "status": "sent",
                    "to": to_number,
                    "message": message
                }
            
            # En producción, enviar real
            msg = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}: {msg.sid}")
            return {
                "success": True,
                "sid": msg.sid,
                "status": msg.status,
                "to": to_number
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {"success": False, "error": str(e)}
    
    def make_voice_call(self, to_number: str, message: str) -> Dict:
        """Realizar una llamada de voz"""
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            # URL del webhook de nuestro servidor
            webhook_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
            
            # En desarrollo, simular
            if os.getenv("ENVIRONMENT") == "development":
                logger.info(f"📞 [DEV] Call would be made to {to_number}")
                return {
                    "success": True,
                    "sid": "dev_call_" + to_number[-8:],
                    "status": "queued",
                    "message": f"Simulated call to {to_number}"
                }
            
            # En producción, llamada real
            call = self.client.calls.create(
                url=f"{webhook_url}/api/v1/webhooks/twilio/outgoing-call",
                to=to_number,
                from_=self.phone_number,
                method="GET"
            )
            
            logger.info(f"Call initiated to {to_number}: {call.sid}")
            return {
                "success": True,
                "sid": call.sid,
                "status": call.status,
                "to": to_number
            }
            
        except Exception as e:
            logger.error(f"Error making call: {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_balance(self) -> Dict:
        """Obtener balance de la cuenta Twilio"""
        if not self.client:
            return {"success": False, "error": "Twilio not configured"}
        
        try:
            # En Twilio, necesitas usar la API de balance
            # Esta es una simplificación
            return {
                "success": True,
                "balance": "Consulta en https://www.twilio.com/console",
                "currency": "USD",
                "message": "Visita el dashboard de Twilio para ver saldo exacto"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Instancia global
twilio_service = TwilioRealService()
