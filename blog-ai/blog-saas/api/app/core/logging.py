"""
Structured logging via structlog.

Output format is auto-selected:
- LOG_FORMAT=json (default in prod) → JSON lines for Railway/Sentry ingestion
- LOG_FORMAT=console               → pretty colored output for local dev

Usage:
    from app.core.logging import get_logger
    log = get_logger(__name__)
    log.info("coin_purchase_credited", user_id=42, coins=500, session_id="cs_x")

Always pass structured key=value pairs instead of formatting strings —
the keys become indexable fields in any log aggregator.

Request correlation: a request_id contextvar is bound per HTTP request
by RequestIdMiddleware (wired in main.py) so every log line emitted
during that request carries the same id.
"""
from __future__ import annotations

import logging
import os
import sys

import structlog
from structlog.contextvars import merge_contextvars

_CONFIGURED = False


def configure_logging() -> None:
    """Idempotent. Safe to call from main.py at startup; no-op on repeat calls."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_format = os.getenv("LOG_FORMAT", "").strip().lower()
    if not log_format:
        # Default: console when running interactively, json otherwise
        log_format = "console" if sys.stdout.isatty() else "json"

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Route stdlib logging through structlog so uvicorn/sqlalchemy logs
    # share the same format. Honour the requested level on the root logger.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level, logging.INFO),
    )

    shared_processors = [
        merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level, logging.INFO)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _CONFIGURED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a logger. Auto-configures on first call so tests / scripts that
    skip main.py still get structured output."""
    if not _CONFIGURED:
        configure_logging()
    return structlog.get_logger(name)
