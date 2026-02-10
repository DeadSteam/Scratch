import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from structlog.contextvars import bind_contextvars, clear_contextvars

from .audit import AuditLogMiddleware
from .config import settings
from .logging_config import get_logger
from .metrics import (
    dec_requests_in_progress,
    inc_requests_in_progress,
    observe_http_request,
)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches request_id and basic request context to logs."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))

        bind_contextvars(
            request_id=request_id,
            path=str(request.url.path),
            method=request.method,
            environment=settings.ENVIRONMENT,
        )

        logger = get_logger(__name__)
        logger.info("request_started")

        try:
            response = await call_next(request)
        except Exception:
            # Do not swallow the exception: FastAPI exception handlers will process it,
            # but logs will already contain request_id and context.
            logger.error("request_failed")
            clear_contextvars()
            raise

        response.headers["X-Request-Id"] = request_id
        logger.info("request_finished", status_code=response.status_code)

        clear_contextvars()
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that records basic Prometheus HTTP metrics."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path = request.url.path
        inc_requests_in_progress(method=method, path=path)

        try:
            start = time.perf_counter()
            response = await call_next(request)
            duration = time.perf_counter() - start
            observe_http_request(
                method=method,
                path=path,
                duration=duration,
                status_code=response.status_code,
            )
            return response
        finally:
            dec_requests_in_progress(method=method, path=path)


def register_middlewares(app: FastAPI) -> None:
    """Register all application middlewares in one place."""
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # Audit logging (mutating API requests)
    app.add_middleware(AuditLogMiddleware)

    # Metrics
    app.add_middleware(MetricsMiddleware)

    # Request ID / structured logging
    app.add_middleware(RequestIdMiddleware)
