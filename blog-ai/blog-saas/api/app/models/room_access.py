from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class RoomAccess(Base):
    __tablename__ = "room_access"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_type: Mapped[str] = mapped_column(String(20), nullable=False)  # invited, password_entered, paid
    granted_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
