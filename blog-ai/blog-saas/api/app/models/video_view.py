from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from typing import Optional

class VideoView(Base):
    __tablename__ = "video_views"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # para anónimos
    watch_seconds: Mapped[int] = mapped_column(Integer, default=0)  # segundos vistos
    completed: Mapped[bool] = mapped_column(default=False)  # >80% visto
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
