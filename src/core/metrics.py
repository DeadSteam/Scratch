from fastapi import FastAPI, Response
from opentelemetry import trace
from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from prometheus_client.openmetrics.exposition import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from .config import settings

# Для переменной Application Name в Grafana (label_values(fastapi_app_info{}, app_name))
APP_INFO = Gauge(
    "fastapi_app_info",
    "FastAPI application info for dashboard variable",
    ["app_name"],
)
APP_INFO.labels(app_name=settings.APP_NAME).set(1)

REQUEST_COUNTER = Counter(
    "fastapi_requests_total",
    "Total FastAPI HTTP requests",
    ["method", "path", "app_name"],
)

REQUEST_LATENCY = Histogram(
    "fastapi_requests_duration_seconds",
    "FastAPI HTTP request latency in seconds",
    ["method", "path", "app_name"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

RESPONSES_COUNTER = Counter(
    "fastapi_responses_total",
    "Total FastAPI HTTP responses by status code",
    ["method", "path", "status_code", "app_name"],
)

EXCEPTIONS_COUNTER = Counter(
    "fastapi_exceptions_total",
    "Total unhandled exceptions",
    ["app_name"],
)

REQUESTS_IN_PROGRESS = Gauge(
    "fastapi_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "path", "app_name"],
)


def observe_http_request(
    method: str,
    path: str,
    duration: float,
    status_code: int,
) -> None:
    """Record HTTP metrics with exemplar pointing to current trace when available."""
    app_name = settings.APP_NAME
    status_str = str(status_code)

    REQUEST_COUNTER.labels(method=method, path=path, app_name=app_name).inc()
    RESPONSES_COUNTER.labels(
        method=method, path=path, status_code=status_str, app_name=app_name
    ).inc()

    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.is_valid:
        trace_id = trace.format_trace_id(ctx.trace_id)
        REQUEST_LATENCY.labels(
            method=method,
            path=path,
            app_name=app_name,
        ).observe(duration, exemplar={"TraceID": trace_id})
    else:
        REQUEST_LATENCY.labels(
            method=method,
            path=path,
            app_name=app_name,
        ).observe(duration)


def record_exception() -> None:
    """Increment exception counter."""
    EXCEPTIONS_COUNTER.labels(app_name=settings.APP_NAME).inc()


def inc_requests_in_progress(method: str, path: str) -> None:
    """Increment in-progress requests gauge."""
    REQUESTS_IN_PROGRESS.labels(
        method=method, path=path, app_name=settings.APP_NAME
    ).inc()


def dec_requests_in_progress(method: str, path: str) -> None:
    """Decrement in-progress requests gauge."""
    REQUESTS_IN_PROGRESS.labels(
        method=method, path=path, app_name=settings.APP_NAME
    ).dec()


def init_metrics(app: FastAPI) -> None:
    """Expose Prometheus /metrics endpoint with OpenMetrics format."""

    @app.get("/metrics")
    async def metrics() -> Response:
        data = generate_latest(REGISTRY)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
