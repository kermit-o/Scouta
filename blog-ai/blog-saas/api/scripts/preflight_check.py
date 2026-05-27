#!/usr/bin/env python3
"""
Preflight check for Stripe / Railway / DB config before flipping to live mode
(or just to verify a deploy is wired up correctly).

Run from inside the Railway container:

    railway ssh
    python scripts/preflight_check.py            # checks current mode
    python scripts/preflight_check.py --live     # additionally requires sk_live / pk_live

Exits 0 on green, 1 on any failure. Each check prints PASS / FAIL with
context so you can tell what's wrong without reading the source.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable

# Make `import app.*` work when running this script directly from anywhere
# inside the repo. We climb up until we find pyproject.toml / requirements.txt.
_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE.parent, _HERE.parent.parent):
    if (_candidate / "requirements.txt").exists():
        sys.path.insert(0, str(_candidate))
        break


# ---------- pretty printing ----------

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"

failures: list[str] = []
warnings: list[str] = []


def ok(msg: str) -> None:
    print(f"  {GREEN}PASS{RESET}  {msg}")


def fail(msg: str) -> None:
    print(f"  {RED}FAIL{RESET}  {msg}")
    failures.append(msg)


def warn(msg: str) -> None:
    print(f"  {YELLOW}WARN{RESET}  {msg}")
    warnings.append(msg)


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


# ---------- checks ----------

def check_env(*, require_live: bool) -> None:
    section("Env vars")

    required = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "FRONTEND_URL",
    ]
    for name in required:
        val = os.getenv(name, "")
        if not val:
            fail(f"{name} is empty")
        else:
            ok(f"{name} is set ({len(val)} chars)")

    # JWT secret must not be a known dev placeholder
    jwt = os.getenv("JWT_SECRET_KEY", "")
    insecure_defaults = {
        "",
        "dev-secret",
        "development-secret-key-change-in-production",
        "INSECURE-SET-JWT-SECRET-KEY-IN-ENV",
        "test-secret-key-do-not-use-in-prod",
    }
    if jwt in insecure_defaults:
        fail(f"JWT_SECRET_KEY is a known insecure placeholder ({jwt[:20]!r})")
    elif len(jwt) < 32:
        warn(f"JWT_SECRET_KEY is short ({len(jwt)} chars) — recommend ≥32")

    # Stripe key prefixes must match the requested mode
    sk = os.getenv("STRIPE_SECRET_KEY", "")
    pk = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    expected_prefix_sk = "sk_live_" if require_live else "sk_"  # accept test in non-live
    expected_prefix_pk = "pk_live_" if require_live else "pk_"

    if sk and not sk.startswith(expected_prefix_sk):
        fail(
            f"STRIPE_SECRET_KEY prefix is {sk[:7]!r}, "
            f"expected {expected_prefix_sk!r}"
        )
    elif sk:
        mode = "LIVE" if sk.startswith("sk_live_") else "TEST"
        ok(f"STRIPE_SECRET_KEY mode = {mode}")

    if pk and not pk.startswith(expected_prefix_pk):
        fail(
            f"STRIPE_PUBLISHABLE_KEY prefix is {pk[:7]!r}, "
            f"expected {expected_prefix_pk!r}"
        )
    elif pk:
        mode = "LIVE" if pk.startswith("pk_live_") else "TEST"
        ok(f"STRIPE_PUBLISHABLE_KEY mode = {mode}")

    # Mode coherence: sk and pk must match
    if sk and pk:
        sk_live = sk.startswith("sk_live_")
        pk_live = pk.startswith("pk_live_")
        if sk_live != pk_live:
            fail(
                "STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY are in DIFFERENT modes "
                f"(sk={'live' if sk_live else 'test'}, pk={'live' if pk_live else 'test'})"
            )
        else:
            ok("Stripe sk + pk modes match")

    # Webhook secret looks right
    whsec = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if whsec and not whsec.startswith("whsec_"):
        fail(f"STRIPE_WEBHOOK_SECRET prefix is {whsec[:7]!r}, expected 'whsec_'")
    elif whsec:
        ok("STRIPE_WEBHOOK_SECRET shape looks right")

    # The split-secret hygiene check (live mode only)
    billing_whsec = os.getenv("STRIPE_BILLING_WEBHOOK_SECRET", "")
    if require_live:
        if not billing_whsec:
            fail(
                "STRIPE_BILLING_WEBHOOK_SECRET is empty. In live mode each "
                "Stripe webhook endpoint has its own secret — billing.py "
                "needs its own. See STRIPE_LIVE_MIGRATION.md."
            )
        elif not billing_whsec.startswith("whsec_"):
            fail(
                f"STRIPE_BILLING_WEBHOOK_SECRET prefix is {billing_whsec[:7]!r}, "
                "expected 'whsec_'"
            )
        else:
            ok("STRIPE_BILLING_WEBHOOK_SECRET is set")
    else:
        if billing_whsec:
            ok("STRIPE_BILLING_WEBHOOK_SECRET is set (good)")
        else:
            warn(
                "STRIPE_BILLING_WEBHOOK_SECRET is not set — fine in test mode "
                "with a single shared endpoint, but required for live"
            )


def check_db_plans(*, require_live: bool) -> None:
    section("DB: plans table")
    try:
        from app.core.db import SessionLocal
        from app.models.plan import Plan
    except Exception as e:  # pragma: no cover
        fail(f"could not import app modules: {e}")
        return

    db = SessionLocal()
    try:
        plans = db.query(Plan).order_by(Plan.id).all()
        if len(plans) < 3:
            fail(f"expected at least 3 plans (free/creator/brand), got {len(plans)}")

        for p in plans:
            if p.id == 1:
                # free plan — no stripe_price_id needed
                continue
            if not p.stripe_price_id:
                fail(f"Plan id={p.id} ({p.name}) has empty stripe_price_id")
                continue
            mode = (
                "LIVE" if p.stripe_price_id.startswith("price_") and "test_" not in p.stripe_price_id
                else "TEST"
            )
            # Stripe live price IDs don't have a "test_" infix, but the most
            # reliable signal is the sk we saw above. We just print mode here
            # as a hint and let the user spot mismatches.
            ok(f"Plan id={p.id} ({p.name}) stripe_price_id is set: {p.stripe_price_id[:20]}...")

            if require_live and "test" in p.stripe_price_id.lower():
                fail(
                    f"Plan id={p.id} stripe_price_id contains 'test'. "
                    "Update to live price IDs."
                )
    finally:
        db.close()


def check_db_connectivity() -> None:
    section("DB: connectivity")
    try:
        from sqlalchemy import text
        from app.core.db import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        ok("DB SELECT 1 succeeded")
    except Exception as e:
        fail(f"DB query failed: {e}")


def check_alembic_head() -> None:
    section("DB: alembic version")
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from sqlalchemy import text
        from app.core.db import engine

        cfg = Config("alembic.ini")
        sd = ScriptDirectory.from_config(cfg)
        heads = list(sd.get_heads())
        if len(heads) != 1:
            fail(f"alembic graph has {len(heads)} heads — must be exactly 1")
            return

        with engine.connect() as conn:
            row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).first()
            current = row[0] if row else None

        if not current:
            fail("alembic_version table is empty — DB not stamped")
        elif current != heads[0]:
            fail(f"current alembic revision = {current!r}, but head = {heads[0]!r}")
        else:
            ok(f"alembic at head ({current})")
    except Exception as e:
        warn(f"alembic check skipped: {e}")


def check_imports() -> None:
    section("App imports")
    try:
        import app.main  # noqa: F401
        ok("app.main imported cleanly")
    except Exception as e:
        fail(f"app.main import failed: {e}")


# ---------- main ----------

def main(argv: Iterable[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Require live-mode keys (sk_live_, pk_live_). Use right before flipping to live.",
    )
    args = parser.parse_args(list(argv))

    print(f"Preflight check — mode: {'LIVE' if args.live else 'CURRENT'}")

    check_env(require_live=args.live)
    check_db_connectivity()
    check_alembic_head()
    check_db_plans(require_live=args.live)
    check_imports()

    print()
    if failures:
        print(f"{RED}{len(failures)} FAILURE(S):{RESET}")
        for f in failures:
            print(f"  - {f}")
    if warnings:
        print(f"{YELLOW}{len(warnings)} warning(s):{RESET}")
        for w in warnings:
            print(f"  - {w}")
    if not failures:
        print(f"{GREEN}OK{RESET} — preflight passed")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
