from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class PlatformEarnings(Base):
    __tablename__ = "platform_earnings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stream_room_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    gift_send_id: Mapped[int] = mapped_column(Integer, ForeignKey("gift_sends.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)      # total gift cost
    fee_amount: Mapped[int] = mapped_column(Integer, nullable=False)  # platform cut (20%)
    host_amount: Mapped[int] = mapped_column(Integer, nullable=False) # host cut (80%)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
