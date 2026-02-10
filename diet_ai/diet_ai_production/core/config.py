"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "DietAI"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dietai_db"
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: Optional[str] = "5432"
    DB_NAME: Optional[str] = "dietai_db"
    DB_USER: Optional[str] = "dietai"
    DB_PASSWORD: Optional[str] = "your_password_here"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    ALLOWED_ORIGINS: Optional[List[str]] = None
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif"]
    
    # AI Services (optional)
    OPENAI_API_KEY: Optional[str] = None
    NUTRITIONIX_API_KEY: Optional[str] = None
    NUTRITIONIX_APP_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar variables extra en .env

settings = Settings()
