from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.db import Base


class CoinTransaction(Base):
    __tablename__ = "coin_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # positive = credit, negative = debit
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # purchase, gift_sent, gift_received, room_entry, refund
    reference_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # stripe payment id, gift id, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
