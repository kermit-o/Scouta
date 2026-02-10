from sqlalchemy import ForeignKey, String, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class OrgMember(Base):
    __tablename__ = "org_members"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uq_org_member_org_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # owner/admin/editor/viewer
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="viewer")

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
