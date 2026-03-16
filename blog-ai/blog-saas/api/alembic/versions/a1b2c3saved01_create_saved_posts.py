"""create saved_posts table

Revision ID: a1b2c3saved01
Revises: 983c49a8265d
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa
from typing import Union

revision: str = "a1b2c3saved01"
down_revision: Union[str, None] = "983c49a8265d"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "saved_posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "post_id", name="uq_saved_user_post"),
    )

def downgrade() -> None:
    op.drop_table("saved_posts")
