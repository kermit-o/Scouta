"""
Application configuration - VERSIÓN SIMPLIFICADA
"""
from typing import Optional

# Configuración simple sin pydantic-settings
class Settings:
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Scouta Blog AI"
    
    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # DeepSeek API (opcional)
    DEEPSEEK_API_KEY: str = ""
    
    def __init__(self):
        # Intentar cargar desde .env si existe
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
            self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
            self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", self.DEEPSEEK_API_KEY)
        except ImportError:
            pass  # Sin dotenv, usar valores por defecto

settings = Settings()
