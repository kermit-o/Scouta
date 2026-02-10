from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_in_sec: int


class InMemoryRateLimiter:
    """
    Minimal in-memory limiter.
    Keyed by (org_id, bucket_name).
    Not distributed, but good enough for MVP and Codespaces.
    """
    def __init__(self) -> None:
        self._buckets: Dict[Tuple[int, str], Tuple[int, float]] = {}

    def hit(self, org_id: int, bucket: str, limit: int, window_sec: int) -> RateLimitResult:
        now = time.time()
        key = (org_id, bucket)
        used, reset_at = self._buckets.get(key, (0, now + window_sec))

        # window expired
        if now >= reset_at:
            used, reset_at = 0, now + window_sec

        if used >= limit:
            return RateLimitResult(allowed=False, remaining=0, reset_in_sec=max(1, int(reset_at - now)))

        used += 1
        self._buckets[key] = (used, reset_at)
        remaining = max(0, limit - used)
        return RateLimitResult(allowed=True, remaining=remaining, reset_in_sec=max(1, int(reset_at - now)))


limiter = InMemoryRateLimiter()
