from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class OrgUsageDaily(Base):
    __tablename__ = "org_usage_daily"
    __table_args__ = (UniqueConstraint("org_id", "day_utc", name="uq_org_usage_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)
    day_utc: Mapped["Date"] = mapped_column(Date, nullable=False, index=True)

    actions_spawned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actions_published: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
