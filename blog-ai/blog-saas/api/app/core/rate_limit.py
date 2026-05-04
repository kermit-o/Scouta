"""Shared per-IP rate limiter.

This module exists because slowapi's @limiter.limit decorator enforces
rate limits using the storage of whichever Limiter instance the
decorator was called on. If each route module created its own Limiter,
the counter buckets and the exception handler registered in main.py
wouldn't match — result: rate limits silently never fired (which is
exactly what we observed before this change).

One process-wide instance, imported everywhere. The SlowAPIMiddleware
in main.py reads `app.state.limiter` to apply the global default limit
to every route; per-route overrides come from the @limiter.limit
decorators against this same instance.

Note: storage is in-memory and per-process. With N gunicorn workers,
effective limit is N × (configured limit). Acceptable for now — if we
need stricter, swap in slowapi's Redis storage backend.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
