from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    target_type: Mapped[str] = mapped_column(String(20), nullable=False)   # post/comment
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)

    action_type: Mapped[str] = mapped_column(String(30), nullable=False)   # comment/reply/reaction/suggest_edit
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")  # draft/published/blocked/needs_review

    content: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # policy outputs
    policy_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    policy_reason: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    # LLM audit meta (optional)
    llm_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    llm_model: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    prompt_hash: Mapped[str] = mapped_column(String(80), nullable=False, default="")
        # idempotency (optional)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=True, default="", index=True)


    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)

Index("ix_agent_actions_org_status_created", AgentAction.org_id, AgentAction.status, AgentAction.created_at)
