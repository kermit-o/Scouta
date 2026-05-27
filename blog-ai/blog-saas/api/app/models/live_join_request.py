from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class LiveJoinRequest(Base):
    """A viewer's pending request to join a live as co-host. Durable
    replacement for the in-memory _join_requests dict — survives restarts so
    a host doesn't lose pending requests when the API redeploys."""
    __tablename__ = "live_join_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("room_name", "user_id", name="uq_live_join_req_room_user"),
    )
