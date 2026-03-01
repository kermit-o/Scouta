from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Perfil público
    username: Mapped[Optional[str]] = mapped_column(String(60), unique=True, index=True, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, default="")
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    interests: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    website: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, default="")
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="")
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
