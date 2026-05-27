from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class LiveRecording(Base):
    """A recording (VOD) of a live stream, produced by LiveKit Egress to R2.

    Lifecycle of `status`:
      recording  -> egress started, capturing
      processing -> egress stopped, LiveKit finalizing the file
      ready      -> file written to R2, playback_url populated
      failed     -> egress reported an error
    """
    __tablename__ = "live_recordings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    host_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    egress_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="recording", nullable=False)
    file_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)   # R2 object key
    playback_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_live_recordings_host_status", "host_user_id", "status"),
    )
