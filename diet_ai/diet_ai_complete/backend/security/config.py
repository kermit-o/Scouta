"""
Configuración de seguridad JWT
"""
import os
from datetime import timedelta
from typing import Optional

class SecurityConfig:
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dietai-super-secret-key-change-in-production-please")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días
    
    # Password hashing
    PWD_CONTEXT_SCHEMES = ["bcrypt"]
    
    # CORS (si es necesario)
    CORS_ORIGINS = ["*"]
    
    @classmethod
    def get_token_expiry(cls) -> timedelta:
        """Obtener tiempo de expiración del token"""
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @classmethod
    def verify_secret_key(cls):
        """Verificar que la SECRET_KEY no sea la default"""
        if cls.SECRET_KEY == "dietai-super-secret-key-change-in-production-please":
            print("⚠️  ADVERTENCIA: Estás usando la SECRET_KEY por defecto.")
            print("   Cambia la variable de entorno SECRET_KEY en producción.")
        return cls.SECRET_KEY

security_config = SecurityConfig()
