from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserEvent(Base):
    """Append-only product-analytics event log.

    One row per significant user action (signup, login, purchase, gift, etc.).
    `properties` is a JSON blob of event-specific fields. `request_id` ties
    the event back to the structured logs emitted during the same HTTP request.

    This table only grows — never update or delete rows. Aggregate/expire with
    a scheduled job later if volume becomes a concern.
    """
    __tablename__ = "user_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Nullable: some events (e.g. anonymous page actions) have no user.
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    properties: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    request_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    __table_args__ = (
        # Fast "events of type X over time" queries (the common analytics access pattern).
        Index("ix_user_events_type_created", "event_type", "created_at"),
    )
