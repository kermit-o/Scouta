"""merge a1b2c3saved01 + a1c2e3f4g5h6 heads

Two parallel branches accumulated independently:
- a1b2c3saved01: create_saved_posts
- a1c2e3f4g5h6: add_private_room_fields_to_live_streams

This merge has no schema effect — it just collapses the DAG to a single
head so `alembic upgrade head` becomes unambiguous again.

Revision ID: m20260504_unify_heads
Revises: a1b2c3saved01, a1c2e3f4g5h6
Create Date: 2026-05-04
"""
from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "m20260504_unify_heads"
down_revision = ("a1b2c3saved01", "a1c2e3f4g5h6")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: this is a structural merge of two independent branches.
    pass


def downgrade() -> None:
    pass
