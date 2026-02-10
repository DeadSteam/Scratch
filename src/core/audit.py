"""Audit logging middleware and helpers.

Emits structured audit events to the ``audit`` structlog logger for every
mutating API request (POST, PUT, PATCH, DELETE).  Audit entries include:

- ``user_id`` (from JWT, if authenticated)
- ``action`` (HTTP method)
- ``resource`` (URL path)
- ``status_code``
- ``ip`` (client IP, respecting X-Forwarded-For)
- ``request_id``

All events are written via structlog, which means they flow into the
same pipeline as application logs (Loki / stdout).  For long-term
retention or compliance, attach a dedicated file / DB handler in
``logging_config.py``.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from .logging_config import get_logger

# Dedicated audit logger — separate name makes it easy to filter in Loki /
# route to a dedicated sink if needed.
_audit_logger = get_logger("audit")

# HTTP methods that represent state-changing operations.
_MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def _client_ip(request: Request) -> str:
    """Best-effort client IP extraction."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _extract_user_id(request: Request) -> str | None:
    """Try to extract user_id from the request state (set by auth dep)."""
    # FastAPI stores the result of Depends in request.state when using
    # middleware; however, the standard pattern is to parse the JWT here
    # to avoid coupling with the DI layer.
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    try:
        # Lazy import to avoid circular dependency.
        from .security import verify_token

        payload = verify_token(token)
        return payload.get("sub")
    except Exception:
        return None


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware that emits audit log entries for mutating API requests."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Only audit mutating requests targeting the API.
        if (
            request.method not in _MUTATING_METHODS
            or not request.url.path.startswith("/api/")
        ):
            return await call_next(request)

        user_id = _extract_user_id(request)
        start = time.monotonic()

        try:
            response = await call_next(request)
        except Exception:
            _audit_logger.error(
                "audit_event",
                user_id=user_id,
                action=request.method,
                resource=request.url.path,
                ip=_client_ip(request),
                status_code=500,
                duration_ms=_elapsed_ms(start),
                outcome="error",
            )
            raise

        _audit_logger.info(
            "audit_event",
            user_id=user_id,
            action=request.method,
            resource=request.url.path,
            ip=_client_ip(request),
            status_code=response.status_code,
            duration_ms=_elapsed_ms(start),
            outcome="success" if response.status_code < 400 else "failure",
        )
        return response


def _elapsed_ms(start: float) -> float:
    return round((time.monotonic() - start) * 1000, 2)


# ---------------------------------------------------------------------------
# Programmatic audit helper (for service-layer events)
# ---------------------------------------------------------------------------
def emit_audit_event(
    *,
    user_id: str | None,
    action: str,
    resource: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Emit an audit event from application code (not HTTP middleware).

    Use this for business-critical operations that happen outside
    the normal request/response cycle, e.g. background tasks or
    admin CLI commands.
    """
    _audit_logger.info(
        "audit_event",
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        **(details or {}),
    )
