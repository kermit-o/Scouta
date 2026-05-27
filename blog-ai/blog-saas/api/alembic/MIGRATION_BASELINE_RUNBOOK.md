# Alembic Baseline Runbook (May 2026)

## Why this exists

Two issues had been silently growing:

1. **Two heads in parallel**: `a1b2c3saved01` (saved_posts) and
   `a1c2e3f4g5h6` (private_room_fields) branched and never merged.
   `alembic upgrade head` would error on ambiguity.
2. **Drift columns unrecorded**: `app/main.py` had a hand-rolled `[migrate]`
   block that ran `ALTER TABLE … ADD COLUMN` on boot for four columns:
   - `live_streams.thumbnail_url`
   - `coin_wallets.withdrawable_balance`
   - `withdrawal_requests.payout_method`
   - `withdrawal_requests.payout_details`

   These columns exist in the prod DB but no Alembic revision describes
   them — the auto-migration was a workaround for that fact.

Two new revisions fix both:

- `m20260504_unify_heads` — empty merge of the two heads.
- `m20260504_baseline_drift` — idempotent ADD COLUMN for the 4 drift
  columns, guarded by `inspect()` so it's a no-op when the column
  already exists (which is the case in prod today).

After applying, alembic has exactly **1 head** and reality matches
the migration history.

## Apply on Railway

Railway → API service → "Run Command" (or `railway run` from local CLI):

```bash
cd blog-ai/blog-saas/api

# 1. Sanity: see the current revision
alembic current

# 2. Sanity: see the heads alembic knows about (should be 1 after deploy)
alembic heads

# 3. Apply the new revisions. Idempotent — safe to re-run.
alembic upgrade head

# 4. Verify
alembic current
# Expected: m20260504_baseline_drift (head)
```

### If `alembic current` shows nothing

The DB has tables but Alembic has never been initialized against it
(`alembic_version` table is missing). Stamp the last known good
revision before upgrading:

```bash
# Stamp at the point right before the merge — the older saved_posts head:
alembic stamp a1b2c3saved01
# Then upgrade
alembic upgrade head
```

## After the upgrade

Once `alembic current` shows `m20260504_baseline_drift`:

1. Tell the assistant — it will remove the auto-migration block from
   `app/main.py` (lines 65–106 today). All future schema changes go
   through Alembic only.
2. Run `alembic check` (or simply re-deploy and watch boot logs) to
   confirm there's no more `[migrate] added column …` output.

## Rolling back

Both new revisions have working `downgrade()`:

```bash
alembic downgrade -1   # back to m20260504_unify_heads (no-op)
alembic downgrade -1   # back to one of the two prior heads
```

The downgrades are idempotent too — they only drop columns that exist.
