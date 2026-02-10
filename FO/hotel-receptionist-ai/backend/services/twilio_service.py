"""
Servicio para integración con Twilio
"""
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TwilioService:
    """Servicio para manejar operaciones con Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token]):
            logger.warning("Twilio credentials not configured")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """Enviar SMS a un número"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
            
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            logger.info(f"SMS sent to {to_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def make_call(self, to_number: str, message: str) -> bool:
        """Realizar una llamada de salida"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
            
        try:
            call = self.client.calls.create(
                twiml=f'<Response><Say language="es-ES">{message}</Say></Response>',
                to=to_number,
                from_=self.phone_number
            )
            logger.info(f"Call initiated to {to_number}: {call.sid}")
            return True
        except Exception as e:
            logger.error(f"Error making call: {e}")
            return False
    
    @staticmethod
    def create_voice_response(message: str, language: str = "es-ES") -> str:
        """Crear respuesta de voz en formato TwiML"""
        response = VoiceResponse()
        response.say(message, voice="alice", language=language)
        return str(response)
    
    @staticmethod
    def create_menu_response(options: Dict[str, str]) -> str:
        """Crear menú interactivo de voz"""
        response = VoiceResponse()
        
        # Construir mensaje con opciones
        message = "Bienvenido. "
        for key, description in options.items():
            message += f"Para {description}, presione {key}. "
        
        gather = Gather(
            numDigits=1,
            action="/api/v1/webhooks/twilio/menu",
            method="POST",
            timeout=5
        )
        gather.say(message, voice="alice", language="es-ES")
        response.append(gather)
        
        # Si no se presiona nada
        response.say("No recibimos su selección. Por favor llame nuevamente.", 
                    voice="alice", language="es-ES")
        
        return str(response)
