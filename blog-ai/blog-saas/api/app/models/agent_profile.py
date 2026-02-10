from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    __table_args__ = (
        UniqueConstraint("org_id", "handle", name="uq_agent_profiles_org_handle"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)

    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    handle: Mapped[str] = mapped_column(String(60), nullable=False)  # e.g. "skeptic_01"
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    # Text seeds for persona consistency (later could become JSON)
    persona_seed: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Topic hints or style hints (comma-separated for MVP)
    topics: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    style: Mapped[str] = mapped_column(String(200), nullable=False, default="concise")

    # 0..3
    risk_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_shadow_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
