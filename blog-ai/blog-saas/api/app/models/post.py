
"""
Post Model - VERSIÓN CORREGIDA con autoincrement
"""
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.core.db import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Campos de autor
    author_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    author_agent_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    author_type: Mapped[str] = mapped_column(String(20), nullable=False, default="user")

    # Contenido
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    body_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    
    # Extracto y metadatos
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Estado
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")

    # Fechas
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)


Index("ix_posts_org_status_created", Post.org_id, Post.status, Post.created_at)
