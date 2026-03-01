from sqlalchemy import String, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.db import Base

class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)           # free, creator, brand
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, default=0)            # 0, 1900, 7900
    max_agents: Mapped[int] = mapped_column(Integer, default=0)
    max_posts_month: Mapped[int] = mapped_column(Integer, default=10)
    can_create_posts: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
