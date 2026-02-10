import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Forge SaaS"
    ENV: str = os.getenv("ENV", "development")

    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./dev.sqlite3"))
    REDIS_URL: str = Field(default=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    # Integraciones
    DEEPSEEK_API_KEY: str | None = None
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    PRO_PRICE_ID: str | None = None

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
