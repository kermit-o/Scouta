"""merge heads: main's live/baseline lineage + branch's account/safety lineage

After reconciling this branch with main (bringing in the baseline-drift, user
events and live-realtime/recordings migrations), the revision graph had two
open heads:
  - m20260524_live_recordings  (main lineage)
  - m20260526_safety_tables    (this branch: deleted_at + reports + user_blocks)
This empty merge migration unifies them so `alembic upgrade head` resolves to a
single head.

Revision ID: m20260527_merge_heads
Revises: m20260524_live_recordings, m20260526_safety_tables
Create Date: 2026-05-27
"""
from __future__ import annotations

revision = "m20260527_merge_heads"
down_revision = ("m20260524_live_recordings", "m20260526_safety_tables")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
