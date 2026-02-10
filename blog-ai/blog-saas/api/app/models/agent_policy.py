from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class AgentPolicy(Base):
    __tablename__ = "agent_policies"
    __table_args__ = (UniqueConstraint("org_id", name="uq_agent_policies_org_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)

    allow_replies: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_reactions: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_critique: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # 0-100, higher is stricter (we'll use it later)
    max_risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    # if true, all agent outputs go to moderation queue
    require_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # comma-separated banned topics for MVP (later JSON)
    banned_topics: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    auto_approve_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    auto_reject_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    enable_llm_moderation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
