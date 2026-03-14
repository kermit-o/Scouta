"""add_media_url_media_type_to_posts

Revision ID: f5250ae8b247
Revises: prod_20260220
Create Date: 2026-03-07
"""
from alembic import op
import sqlalchemy as sa
from typing import Union

revision: str = "f5250ae8b247"
down_revision: Union[str, None] = "prod_20260220"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("posts", sa.Column("media_url", sa.Text(), nullable=True))
    op.add_column("posts", sa.Column("media_type", sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column("posts", "media_type")
    op.drop_column("posts", "media_url")
