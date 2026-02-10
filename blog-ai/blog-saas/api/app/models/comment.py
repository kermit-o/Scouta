from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)

    parent_comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)

    # human / agent
    author_type: Mapped[str] = mapped_column(String(10), nullable=False)

    author_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    author_agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent_profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    body: Mapped[str] = mapped_column(Text, nullable=False)

    # published / hidden
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

Index("ix_comments_org_post_created", Comment.org_id, Comment.post_id, Comment.created_at)
