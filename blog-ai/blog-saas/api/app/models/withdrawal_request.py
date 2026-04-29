from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.db import Base


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_coins: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)  # USD cents equivalent
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")  # pending, processing, completed, failed
    payout_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # paypal, bank, stripe_connect
    payout_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # email, IBAN+SWIFT, etc.
    stripe_transfer_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True), nullable=True)
