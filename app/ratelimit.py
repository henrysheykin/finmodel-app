"""Per-IP sliding-window rate limits for the public endpoints that create work (E15).

Creating an order builds a brief and writes rows; opening a checkout calls the payment provider.
Both are anonymous, so a script could flood them. Limits are kept in memory: the deployment runs
one web process (ADR-008), and a restart forgetting the counts is harmless.

The client address: see ``client_ip`` (CLIENT_IP_HEADER, docs/DEPLOY.md).
"""

from __future__ import annotations

import math
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request

WINDOW_SECONDS = 600  # 10 minutes
MAX_KEYS = 50_000  # memory bound: when exceeded, idle keys are dropped


class RateLimiter:
    """``hit(bucket, key)`` records one attempt and says whether it is allowed."""

    def __init__(self, limit: int, window: float = WINDOW_SECONDS, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window
        self.clock = clock
        self._hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return self.limit > 0

    def hit(self, bucket: str, key: str) -> float:
        """Record an attempt. Returns 0 when allowed, else the seconds until the next one is."""
        if not self.enabled:
            return 0.0
        now = self.clock()
        with self._lock:
            if len(self._hits) > MAX_KEYS:
                self._sweep(now)
            q = self._hits[(bucket, key)]
            while q and q[0] <= now - self.window:
                q.popleft()
            if len(q) >= self.limit:
                return max(1.0, q[0] + self.window - now)
            q.append(now)
            return 0.0

    def _sweep(self, now: float) -> None:
        for k in [k for k, q in self._hits.items() if not q or q[-1] <= now - self.window]:
            del self._hits[k]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_init_lock = threading.Lock()


def client_ip(request: Request) -> str:
    """The visitor's address: the key of every per-address limit (orders, checkout, magic links,
    admin login — E17 made them all use this one function).

    With CLIENT_IP_HEADER set (e.g. ``X-Real-IP`` on a host whose edge proxy sets it), that header
    wins; otherwise the peer address uvicorn derived from ``X-Forwarded-For`` (its left-most entry,
    because the container trusts every proxy). That is only safe behind an edge that overwrites
    the caller's ``X-Forwarded-For`` (Railway does, and puts the visitor first while the right-most
    entry is an internal hop); on any other host set CLIENT_IP_HEADER, or callers choose their key.
    """
    sv = getattr(request.app.state, "services", None)
    header = sv.cfg.client_ip_header if sv is not None else ""
    if header:
        value = request.headers.get(header, "").split(",")[0].strip()
        if value:
            return value[:64]
    return request.client.host if request.client else "unknown"


def check(request: Request, bucket: str) -> int:
    """0 when the request may go on; otherwise the Retry-After value in whole seconds."""
    limiter: RateLimiter | None = getattr(request.app.state, "limiter", None)
    if limiter is None:  # first request: services (and their settings) exist only after startup
        with _init_lock:
            limiter = getattr(request.app.state, "limiter", None)
            if limiter is None:
                limiter = RateLimiter(request.app.state.services.cfg.rate_limit_per_10min)
                request.app.state.limiter = limiter
    wait = limiter.hit(bucket, client_ip(request))
    return math.ceil(wait) if wait else 0
