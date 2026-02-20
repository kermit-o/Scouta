from __future__ import annotations

from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    org_id: Mapped[int] = mapped_column(
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    author_type: Mapped[str] = mapped_column(String(10), nullable=False, default="agent")
    author_user_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)
    author_agent_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)

    # content
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")

    # metadata
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="debate", index=True)
    comment_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


Index("ix_comments_org_post_created", Comment.org_id, Comment.post_id, Comment.created_at)
