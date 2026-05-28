from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class UserBlock(Base):
    """Account-level block: blocker_user_id hides/blocks blocked_user_id across
    the app (App Store / Google Play UGC requirement)."""
    __tablename__ = "user_blocks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    blocker_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    blocked_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("blocker_user_id", "blocked_user_id", name="uq_user_block"),)
