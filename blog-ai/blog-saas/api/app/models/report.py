from sqlalchemy import ForeignKey, DateTime, func, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.db import Base


class Report(Base):
    """A user-submitted report against UGC or another user (App Store 1.2 /
    Google Play UGC moderation requirement)."""
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reporter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # target_type: user | post | comment | live | message
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # status: open | reviewed | actioned | dismissed
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="open")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_reports_status", "status"),)
