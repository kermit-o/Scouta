"""
RequestIdMiddleware: bind a per-request id into structlog's context so every
log line emitted during the request carries it. Honors an incoming
X-Request-Id header (useful for tracing across hops); otherwise generates
a uuid4. Echoes the id back on the response.
"""
from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from structlog.contextvars import bind_contextvars, clear_contextvars


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        try:
            response = await call_next(request)
        finally:
            clear_contextvars()
        response.headers["x-request-id"] = request_id
        return response
