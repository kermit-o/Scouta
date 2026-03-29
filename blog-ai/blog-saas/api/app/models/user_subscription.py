from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.db import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscriber_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")  # active, canceled, expired
    price_cents: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True), nullable=True)
