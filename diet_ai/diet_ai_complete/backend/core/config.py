import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    api_title: str = "DietAI API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://dietai_user:dietai_pass@localhost:5432/dietai"
    )
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
