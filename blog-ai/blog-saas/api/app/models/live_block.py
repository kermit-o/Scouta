from sqlalchemy import String, Integer, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class LiveBlock(Base):
    """A user blocked from a live room's chat. Durable replacement for the
    old in-memory _blocked_per_room dict (which was lost on every restart)."""
    __tablename__ = "live_blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("room_name", "username", name="uq_live_block_room_user"),
    )
