"""Simple process-local rate limiter for the single-process v1 deployment."""

from collections import defaultdict, deque
from time import monotonic

from app.core.errors import DomainError

_events: dict[str, deque[float]] = defaultdict(deque)


def enforce_rate_limit(key: str, limit: int, window_seconds: int = 60) -> None:
    now = monotonic()
    events = _events[key]
    while events and now - events[0] >= window_seconds:
        events.popleft()
    if len(events) >= limit:
        raise DomainError("RATE_LIMITED", "Too many requests. Try again shortly.")
    events.append(now)
