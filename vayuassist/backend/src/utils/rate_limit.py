"""Small in-process sliding-window rate limiter for the MVP."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

DEFAULT_LIMIT = 10
DEFAULT_WINDOW_SECONDS = 60

_requests: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def check_rate_limit(
    key: str,
    limit: int = DEFAULT_LIMIT,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
) -> tuple[bool, int]:
    """Record a request if allowed and return (allowed, retry_after_seconds)."""
    now = monotonic()
    with _lock:
        entries = _requests[key]
        cutoff = now - window_seconds
        while entries and entries[0] <= cutoff:
            entries.popleft()

        if len(entries) >= limit:
            retry_after = max(1, int(entries[0] + window_seconds - now) + 1)
            return False, retry_after

        entries.append(now)
        return True, 0
