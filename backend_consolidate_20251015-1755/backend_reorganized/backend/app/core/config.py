from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Forge E-commerce Backend"
    database_url: str = "sqlite:///./backend/app/app.db"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
