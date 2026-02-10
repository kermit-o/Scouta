from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - USAR asyncpg en la URL
    DATABASE_URL: str = "postgresql+asyncpg://dietai:dietai123@postgres:5432/dietai"
    
    # JWT
    SECRET_KEY: str = "tu_super_secreto_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # App
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Dieta API"
    VERSION: str = "2.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
