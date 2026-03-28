from sqlalchemy import Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class CoinWallet(Base):
    __tablename__ = "coin_wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    balance: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    lifetime_earned: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    lifetime_spent: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
