"""In-memory login throttling (S-10).

Failed attempts are counted per (client IP, email). After ``max_attempts``
failures inside the window, that pair is locked out until the window expires.
A successful login clears the counter.

Single-process only: with several API replicas this must move to a shared
store (e.g. Redis). Documented in AGENTS.md.
"""
import threading
import time
from dataclasses import dataclass, field


@dataclass
class _Entry:
    failures: list[float] = field(default_factory=list)


class LoginRateLimiter:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], _Entry] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key(ip: str, email: str) -> tuple[str, str]:
        return (ip or "unknown", (email or "").strip().lower())

    def _window(self) -> tuple[int, float]:
        from app.core.config import settings

        return settings.LOGIN_MAX_ATTEMPTS, settings.LOGIN_LOCKOUT_MINUTES * 60.0

    def retry_after(self, ip: str, email: str) -> int:
        """Seconds until the pair may try again; 0 when not locked."""
        max_attempts, window = self._window()
        now = time.monotonic()
        with self._lock:
            entry = self._entries.get(self._key(ip, email))
            if not entry:
                return 0
            entry.failures = [t for t in entry.failures if now - t < window]
            if len(entry.failures) < max_attempts:
                return 0
            return max(1, int(window - (now - entry.failures[0])))

    def register_failure(self, ip: str, email: str) -> None:
        with self._lock:
            self._entries.setdefault(self._key(ip, email), _Entry()).failures.append(time.monotonic())

    def register_success(self, ip: str, email: str) -> None:
        with self._lock:
            self._entries.pop(self._key(ip, email), None)

    def reset(self) -> None:
        with self._lock:
            self._entries.clear()


login_rate_limiter = LoginRateLimiter()
