# config/ai_config.py - VERSIÓN CORREGIDA
import os
from typing import Optional
import logging
from dotenv import load_dotenv

# CARGAR .env EXPLÍCITAMENTE
load_dotenv()

logger = logging.getLogger(__name__)

class AIConfig:
    def __init__(self):
        # Cargar desde .env explícitamente
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
        # Log de diagnóstico
        logger.info(f"🔧 DeepSeek Config - API Key presente: {bool(self.deepseek_api_key)}")
        logger.info(f"🔧 DeepSeek Config - Key length: {len(self.deepseek_api_key)}")
        logger.info(f"🔧 DeepSeek Config - Available: {self.is_available()}")
    
    def is_available(self) -> bool:
        """Verificar si DeepSeek está configurado correctamente"""
        # Verificar que la API key existe y es válida
        is_valid = (self.deepseek_api_key and 
                   self.deepseek_api_key != "your_deepseek_api_key_here" and
                   not self.deepseek_api_key.startswith("your_") and
                   len(self.deepseek_api_key) > 20)
        
        if not is_valid:
            logger.warning(f"❌ DeepSeek no configurado - Key: '{self.deepseek_api_key[:20]}...'")
            logger.warning("💡 Verifica que DEEPSEEK_API_KEY esté en .env y sea válida")
        
        return is_valid
    
    def get_headers(self) -> dict:
        """Obtener headers para requests a DeepSeek"""
        if not self.is_available():
            raise ValueError("DeepSeek no configurado - verifica DEEPSEEK_API_KEY en .env")
            
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }

# Instancia global de configuración
ai_config = AIConfig()