from sqlalchemy import Boolean, ForeignKey, Integer, Float, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class OrgSettings(Base):
    __tablename__ = "org_settings"
    __table_args__ = (UniqueConstraint("org_id", name="uq_org_settings_org_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)

    agents_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_publish: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    max_agents_per_post: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    max_actions_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    # 0.0 - 1.0 probability baseline
    spawn_probability_base: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)

    # optional: "en", "es", "fr"
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="es")

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
