"""Circuit breaker pattern for external service calls.

Prevents cascading failures by failing fast when a downstream service
is unavailable.  After ``recovery_timeout`` seconds the breaker moves
to HALF-OPEN and lets a single probe request through.

Usage
-----
::

    cb = CircuitBreaker(name="redis", failure_threshold=5)

    async def do_work():
        cb.ensure_closed()           # raises CircuitOpenError if open
        try:
            result = await call_external()
            cb.record_success()
            return result
        except Exception as exc:
            cb.record_failure()
            raise

Or as a decorator::

    @circuit_breaker(name="redis", failure_threshold=5)
    async def call_redis():
        ...
"""

from __future__ import annotations

import enum
import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

from ..core.logging_config import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when calling through an open circuit breaker."""

    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit '{name}' is OPEN. Retry after {retry_after:.1f}s"
        )


class CircuitBreaker:
    """Thread-safe (asyncio-safe) circuit breaker.

    Parameters
    ----------
    name:
        Human-readable identifier for logging.
    failure_threshold:
        Number of consecutive failures before the circuit opens.
    recovery_timeout:
        Seconds to wait before moving from OPEN → HALF_OPEN.
    success_threshold:
        Successful calls in HALF_OPEN to move back to CLOSED.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0

    # -- public API ---------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        """Current state (evaluates timeout for OPEN → HALF_OPEN)."""
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                logger.info(
                    "circuit_half_open",
                    circuit=self.name,
                    elapsed=round(elapsed, 1),
                )
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
        return self._state

    def ensure_closed(self) -> None:
        """Raise :class:`CircuitOpenError` if the circuit is open."""
        current = self.state
        if current == CircuitState.OPEN:
            retry_after = (
                self.recovery_timeout
                - (time.monotonic() - self._last_failure_time)
            )
            raise CircuitOpenError(self.name, max(retry_after, 0))

    def record_success(self) -> None:
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                logger.info(
                    "circuit_closed",
                    circuit=self.name,
                    after_successes=self._success_count,
                )
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
        else:
            # Reset failure streak on any success in CLOSED state.
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            # Probe failed — go back to OPEN.
            logger.warning(
                "circuit_reopened",
                circuit=self.name,
            )
            self._state = CircuitState.OPEN
            self._success_count = 0
        elif self._failure_count >= self.failure_threshold:
            logger.error(
                "circuit_opened",
                circuit=self.name,
                failures=self._failure_count,
            )
            self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Manually reset the breaker to CLOSED."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0


# ---------------------------------------------------------------------------
# Registry of named circuit breakers (global singletons).
# ---------------------------------------------------------------------------
_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    success_threshold: int = 2,
) -> CircuitBreaker:
    """Get or create a named circuit breaker (singleton per name)."""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold,
        )
    return _breakers[name]


# ---------------------------------------------------------------------------
# Decorator shortcut
# ---------------------------------------------------------------------------
def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    success_threshold: int = 2,
    fallback: Any = None,
) -> Callable[[F], F]:
    """Decorator that wraps an async function with a circuit breaker.

    Parameters
    ----------
    fallback:
        Value to return when the circuit is open instead of raising.
        If ``None``, :class:`CircuitOpenError` is raised.
    """
    cb = get_circuit_breaker(
        name, failure_threshold, recovery_timeout, success_threshold
    )

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                cb.ensure_closed()
            except CircuitOpenError:
                if fallback is not None:
                    return fallback
                raise

            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception:
                cb.record_failure()
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
