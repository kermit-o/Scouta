from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class GiftCatalog(Base):
    __tablename__ = "gift_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False)
    coin_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    animation_type: Mapped[str] = mapped_column(String(20), nullable=False, default="float")  # float, burst, fullscreen
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class GiftSend(Base):
    __tablename__ = "gift_sends"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stream_room_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sender_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    gift_id: Mapped[int] = mapped_column(Integer, ForeignKey("gift_catalog.id"), nullable=False)
    coin_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Seed gift catalog on startup ─────────────────────────────────────────────
GIFT_SEED = [
    {"name": "Rose",    "emoji": "\U0001f339", "coin_cost": 1,   "animation_type": "float",      "sort_order": 1},
    {"name": "Heart",   "emoji": "\u2764\ufe0f",  "coin_cost": 5,   "animation_type": "float",      "sort_order": 2},
    {"name": "Star",    "emoji": "\u2b50",      "coin_cost": 10,  "animation_type": "burst",      "sort_order": 3},
    {"name": "Rocket",  "emoji": "\U0001f680", "coin_cost": 50,  "animation_type": "burst",      "sort_order": 4},
    {"name": "Crown",   "emoji": "\U0001f451", "coin_cost": 100, "animation_type": "fullscreen", "sort_order": 5},
    {"name": "Diamond", "emoji": "\U0001f48e", "coin_cost": 500, "animation_type": "fullscreen", "sort_order": 6},
]


def seed_gift_catalog(db):
    """Insert default gifts if the table is empty. Call on startup."""
    count = db.query(GiftCatalog).count()
    if count == 0:
        from app.core.logging import get_logger
        for g in GIFT_SEED:
            db.add(GiftCatalog(**g))
        db.commit()
        get_logger(__name__).info("gift_catalog_seeded", count=len(GIFT_SEED))
