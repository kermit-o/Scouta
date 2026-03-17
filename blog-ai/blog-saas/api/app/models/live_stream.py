from sqlalchemy import ForeignKey, DateTime, func, String, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from typing import Optional

class LiveStream(Base):
    __tablename__ = "live_streams"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    host_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="live")  # live | ended
    viewer_count: Mapped[int] = mapped_column(Integer, default=0)
    max_viewers: Mapped[int] = mapped_column(Integer, default=0)
    org_id: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
