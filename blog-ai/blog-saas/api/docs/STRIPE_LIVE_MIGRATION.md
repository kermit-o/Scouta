# Stripe Live Mode Migration Runbook

Last updated: 2026-05-04. Author: handed off from claude session.

## TL;DR

Going live = swapping 4 env vars + creating live equivalents of every Stripe
object you have in test mode. The code is mode-agnostic — it just uses
whatever keys you give it. The danger is in mismatched config (live key
pointing at test webhook, etc.).

**There is one known config gap that must be fixed before flipping** —
see "Webhook secret split" below.

---

## Pre-flight checklist

Verify each item BEFORE touching env vars. Skipping any of these is how
you accept real money and have nowhere to send it.

### Stripe account

- [ ] Stripe account is verified (`Activate payments` is green, not pending)
- [ ] Business entity registered in Stripe (Settings → Business)
- [ ] Bank account or external account added for payouts (Settings → Payouts)
- [ ] Tax registration completed if applicable (VAT, IVA)
- [ ] Identity verification (KYC) for the platform owner is approved
- [ ] **Connect platform** is enabled if you plan to onboard hosts for
      withdrawals via Stripe Connect (Settings → Connect)

### Stripe live products & prices

The DB column `Plan.stripe_price_id` is the bridge between our `Plan` rows
and Stripe Prices. Test-mode price IDs do NOT work in live mode — Stripe
returns "No such price". You must:

- [ ] In Stripe dashboard (live mode), create the equivalents of:
  - `creator` plan ($19/mo) → record live `price_id`
  - `brand` plan ($79/mo) → record live `price_id`
  - Coin packages do NOT need Stripe products — `coins.py` builds the
    Checkout Session inline with `price_data.unit_amount`. No DB column
    to update for those.
- [ ] Update `plans` table:
  ```sql
  UPDATE plans SET stripe_price_id = 'price_LIVE_creator_xxx' WHERE id = 2;
  UPDATE plans SET stripe_price_id = 'price_LIVE_brand_xxx'   WHERE id = 3;
  ```
  Do this AFTER you've flipped the env vars and verified live mode is
  active (so app reloads with the right key when querying the DB).
  Better: run from `railway ssh` so you're inside the container.

### Webhook endpoints (CRITICAL — read carefully)

The codebase has **two separate webhook routes**:

| Path | Handler | Events |
|------|---------|--------|
| `/api/v1/coins/stripe-webhook` | `coins.py` | `checkout.session.completed` (coin purchases) |
| `/api/v1/billing/webhook`      | `billing.py` | `invoice.payment_succeeded`, `customer.subscription.deleted`, `payment_intent.succeeded` (subscriptions + legacy coin path) |

**Today both routes read the same env var `STRIPE_WEBHOOK_SECRET`.** In
test mode you got away with this because you have a single webhook endpoint
configured. If you create TWO live webhook endpoints (one per route, which
is the right thing to do), Stripe will issue TWO distinct signing secrets
and our code will only know one of them — half the events will get
`invalid_signature` (400) silently.

**Fix BEFORE going live (small code change, do this first):**

Either:
- **A. Single endpoint, fan-out events** (simplest, if you can): Configure
  ONE Stripe webhook endpoint that points at — pick one — listening to
  all events you care about. Then make the other route reuse the same
  handler logic OR delete one. (Today both paths are wired and active.)
- **B. Two endpoints, two secrets**: Add a second env var
  `STRIPE_BILLING_WEBHOOK_SECRET` and update `billing.py` to read it.
  Each Stripe endpoint gets its own secret in Railway.

Recommended: **B** — it matches Stripe best practice (one endpoint per
URL, one secret per endpoint). Coordinate this code change before the
live flip.

- [ ] Code change for split secrets is merged + deployed
- [ ] Live webhook endpoint A: `https://api.scouta.co/api/v1/coins/stripe-webhook`
      listening to `checkout.session.completed` → record live `whsec_...`
- [ ] Live webhook endpoint B: `https://api.scouta.co/api/v1/billing/webhook`
      listening to `invoice.payment_succeeded`, `customer.subscription.deleted`,
      `customer.subscription.updated`, `invoice.payment_failed`,
      `payment_intent.succeeded` → record live `whsec_...`

### Code health on `main`

- [ ] CI green on the commit you're about to deploy (compileall + 85
      pytest tests + frontend build)
- [ ] Sentry is collecting events from production (test by triggering
      a 500 deliberately and confirming it shows up)
- [ ] `/health/ready` returns 200 (DB probe passing)
- [ ] Latest test-mode E2E manually walked through:
  - [ ] User registers → email arrives → verifies → logs in
  - [ ] User buys 100 coins → wallet shows 100
  - [ ] User sends a 10-coin gift in a live → host's wallet shows 8 (after 20% fee)
  - [ ] User requests a 500-coin withdrawal → admin can approve/reject
  - [ ] User subscribes to creator plan → `/billing/me` shows active

### Backups

- [ ] Take a full snapshot of Railway env vars BEFORE editing
      (`railway variables --json > env-backup-$(date +%Y%m%d).json`)
- [ ] Confirm Postgres has automated backups enabled (Railway → Postgres
      service → "Backups" tab — should show recent timestamps)

---

## The flip (do this in one focused session)

Total time: ~15 minutes once everything above is checked.

### 1. Get all live values ready (don't edit Railway yet)

Open `STRIPE_LIVE_MIGRATION.tmp` (a scratch file) and paste:

```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_LIVE_coins_...        # endpoint A (coins)
STRIPE_BILLING_WEBHOOK_SECRET=whsec_LIVE_billing_...  # endpoint B
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...    # for Vercel
```

Plus the live price IDs:
```
PLAN_2_PRICE_ID=price_live_creator_...
PLAN_3_PRICE_ID=price_live_brand_...
```

DELETE this scratch file once flip is done.

### 2. Update Railway (backend)

Railway → Scouta service → Variables. Edit (NOT delete-and-recreate, which
would empty the var briefly and trigger an outage):

- `STRIPE_SECRET_KEY` → `sk_live_...`
- `STRIPE_PUBLISHABLE_KEY` → `pk_live_...`
- `STRIPE_WEBHOOK_SECRET` → `whsec_LIVE_coins_...`
- `STRIPE_BILLING_WEBHOOK_SECRET` → `whsec_LIVE_billing_...` (new var)

Save. Railway redeploys automatically. Wait for green deploy.

### 3. Update frontend (Vercel)

Vercel → project → Settings → Environment Variables:

- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` → `pk_live_...`

Trigger a redeploy.

### 4. Update DB plans

`railway ssh` → inside container:

```bash
psql $DATABASE_URL -c "UPDATE plans SET stripe_price_id = 'price_live_creator_...' WHERE id = 2;"
psql $DATABASE_URL -c "UPDATE plans SET stripe_price_id = 'price_live_brand_...'   WHERE id = 3;"
psql $DATABASE_URL -c "SELECT id, name, stripe_price_id FROM plans;"
```

### 5. Smoke test the diag endpoint

```bash
curl https://api.scouta.co/api/v1/billing/diag
```

Expected:
```json
{
  "stripe_secret_set": true,
  "stripe_secret_prefix": "sk_live",       <-- key check
  "stripe_pub_set": true,
  "env_stripe_secret": true,
  "env_stripe_prefix": "sk_live"
}
```

If you see `sk_test`, the var didn't update. STOP. Fix Railway and retry.

---

## Post-flip canary (real money, real card)

You're now live. Validate before announcing.

### Coin purchase canary ($1)

Use a personal card (not the platform card). The flow:

1. Log into a real user account on production
2. Wallet → Buy → smallest pack (`pack_100` = $0.99)
3. Stripe Checkout opens, pay with real card
4. Redirect back to wallet
5. Within ~5 seconds, balance should show 100 coins

In Railway logs, search for `stripe_webhook_credited`:
```json
{
  "event": "stripe_webhook_credited",
  "session_id": "cs_live_...",
  "user_id": <your_user_id>,
  "coins": 100,
  "amount_cents": 99,
  "request_id": "..."
}
```

If you don't see it, search for `stripe_webhook_invalid_signature` —
that's the smoking gun for webhook secret mismatch.

In Stripe dashboard (live mode):
- Payments → should show the $0.99 charge as `succeeded`
- Webhooks → endpoint A → should show recent delivery as `200`

### Subscription canary ($19, optional)

Same idea for the subscription path: subscribe to creator plan, watch
for `stripe_webhook_*` and the Plan/Org bump in DB.

You can refund the canary purchases from Stripe dashboard immediately
after verifying. Coins on the test user are technically real now —
deduct manually from the DB if you care:
```sql
UPDATE coin_wallets SET balance = balance - 100 WHERE user_id = <your_user_id>;
```

---

## Monitoring (after going live)

### Sentry alerts to set up

Sentry → Alerts → Create alert. Suggested rules:

- **Webhook signature mismatch**: log message contains
  `stripe_webhook_invalid_signature` → alert immediately. Could be a
  config drift or an attack.
- **Failed coin credit**: log message `stripe_webhook_*` with level
  `error`. Should be near zero in steady state.
- **Subscription create failure**: any 5xx on `/billing/create-payment-intent`.
- **Withdrawal admin error**: 5xx on `/coins/admin/withdrawals/*`.

### Daily reconciliation (manual at first)

Compare Stripe payment count to our `CoinTransaction` purchase count:

```sql
SELECT DATE(created_at) AS day,
       COUNT(*) AS app_purchases,
       SUM(amount) AS coins_credited
FROM coin_transactions
WHERE type = 'purchase' AND created_at > NOW() - INTERVAL '7 days'
GROUP BY 1 ORDER BY 1 DESC;
```

vs Stripe dashboard → Payments → filter last 7 days → count of `succeeded`
charges. They should match exactly. A divergence ≥1 = a webhook didn't
land or didn't credit; investigate.

---

## Rollback

If something is wrong and you can't fix in <30 min:

1. Refund any live charges from Stripe dashboard (one-by-one or bulk)
2. Restore the test-mode env vars from `env-backup-YYYYMMDD.json`:
   - `STRIPE_SECRET_KEY` back to `sk_test_...`
   - `STRIPE_PUBLISHABLE_KEY` back to `pk_test_...`
   - `STRIPE_WEBHOOK_SECRET` back to test secret
   - `STRIPE_BILLING_WEBHOOK_SECRET` back to test secret (or unset, since
     test mode currently uses one secret for both)
3. Frontend `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` back to `pk_test_...`
4. DB:
   ```sql
   UPDATE plans SET stripe_price_id = 'price_test_creator_...' WHERE id = 2;
   UPDATE plans SET stripe_price_id = 'price_test_brand_...'   WHERE id = 3;
   ```
5. Wait for Railway + Vercel redeploys
6. Verify `/billing/diag` shows `sk_test` again
7. Investigate root cause OFFLINE

If the issue is a single bad credit (coins given away) and not a system
failure, just refund the charge in Stripe and adjust the wallet manually.
Don't roll back env vars over a single bad row.

---

## When to actually flip

Honest gate: don't flip until you can answer "yes" to all of these.

- The product has been in test mode long enough that you've found and
  fixed surprises (webhook delivery delays, partial payments, etc.).
- You have at least one user OTHER than yourself who will buy something
  in the first 24 hours, so canary issues don't sit unexplored.
- You have time to babysit Sentry + Stripe dashboard for the first few
  hours.
- You have a way to be reached if something breaks (phone, not just email).

Until those are true, stay in test. Real money creates real obligations
(tax, refunds, chargebacks). The code is ready; the *operation* might not
be.
