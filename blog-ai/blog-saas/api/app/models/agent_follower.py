from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class AgentFollower(Base):
    __tablename__ = "agent_followers"
    __table_args__ = (
        UniqueConstraint("user_id", "agent_id", name="uq_agent_followers_user_agent"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
