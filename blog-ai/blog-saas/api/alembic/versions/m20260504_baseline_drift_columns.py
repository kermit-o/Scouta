"""baseline drift columns added by main.py auto-migration

Backfills Alembic for four columns that were added to live tables by the
hand-rolled `[migrate]` block in app/main.py and never recorded in any
migration:

- live_streams.thumbnail_url       TEXT
- coin_wallets.withdrawable_balance INTEGER DEFAULT 0
- withdrawal_requests.payout_method  VARCHAR(20)
- withdrawal_requests.payout_details TEXT

Idempotent: each ADD COLUMN is guarded by inspect() so it's a no-op on
environments where the auto-migration already applied it (which today
includes prod). After this lands and Alembic is at this head, we can
delete the auto-migration block from main.py.

Revision ID: m20260504_baseline_drift
Revises: m20260504_unify_heads
Create Date: 2026-05-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "m20260504_baseline_drift"
down_revision = "m20260504_unify_heads"
branch_labels = None
depends_on = None


def _has_column(conn, table: str, col: str) -> bool:
    insp = inspect(conn)
    try:
        return any(c["name"] == col for c in insp.get_columns(table))
    except Exception:
        return False


def _table_exists(conn, table: str) -> bool:
    insp = inspect(conn)
    try:
        return table in insp.get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()

    if _table_exists(conn, "live_streams") and not _has_column(conn, "live_streams", "thumbnail_url"):
        op.add_column("live_streams", sa.Column("thumbnail_url", sa.Text(), nullable=True))

    if _table_exists(conn, "coin_wallets") and not _has_column(conn, "coin_wallets", "withdrawable_balance"):
        op.add_column(
            "coin_wallets",
            sa.Column("withdrawable_balance", sa.Integer(), nullable=False, server_default="0"),
        )

    if _table_exists(conn, "withdrawal_requests"):
        if not _has_column(conn, "withdrawal_requests", "payout_method"):
            op.add_column(
                "withdrawal_requests",
                sa.Column("payout_method", sa.String(length=20), nullable=True),
            )
        if not _has_column(conn, "withdrawal_requests", "payout_details"):
            op.add_column(
                "withdrawal_requests",
                sa.Column("payout_details", sa.Text(), nullable=True),
            )


def downgrade() -> None:
    conn = op.get_bind()

    if _table_exists(conn, "withdrawal_requests"):
        if _has_column(conn, "withdrawal_requests", "payout_details"):
            op.drop_column("withdrawal_requests", "payout_details")
        if _has_column(conn, "withdrawal_requests", "payout_method"):
            op.drop_column("withdrawal_requests", "payout_method")

    if _table_exists(conn, "coin_wallets") and _has_column(conn, "coin_wallets", "withdrawable_balance"):
        op.drop_column("coin_wallets", "withdrawable_balance")

    if _table_exists(conn, "live_streams") and _has_column(conn, "live_streams", "thumbnail_url"):
        op.drop_column("live_streams", "thumbnail_url")
