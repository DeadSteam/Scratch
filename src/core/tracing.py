"""OpenTelemetry tracing setup.

Two entry points:

- ``init_tracing(app)`` is called by the FastAPI process at startup.
  It instruments FastAPI, SQLAlchemy and Redis.

- ``init_tracing_for_worker()`` is called inside each Celery worker
  process (via ``worker_process_init.connect``). It re-creates the
  TracerProvider in the worker (a different process from FastAPI) and
  attaches the Celery instrumentor so spans propagate from HTTP through
  RabbitMQ into the worker.

Sampling:
    Controlled by ``TRACING_SAMPLE_RATE`` in config. ``ParentBased``
    means a child request follows the parent's decision — so a single
    sampled trace stays connected end-to-end even when the request fans
    out to a Celery task.
"""

from __future__ import annotations

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF,
    ALWAYS_ON,
    ParentBased,
    TraceIdRatioBased,
)
from opentelemetry.trace import Tracer
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import settings
from .database import knowledge_engine, main_engine, users_engine

# Global tracer used by services for manual span creation. Initialized
# during init_tracing(); falls back to the no-op tracer until then.
_tracer: Tracer = trace.get_tracer("scratch")


def get_tracer() -> Tracer:
    """Return the application tracer.

    Use for manual instrumentation:

        from src.core.tracing import get_tracer

        with get_tracer().start_as_current_span("my_operation"):
            ...
    """
    return _tracer


def _build_sampler():
    """Build a ParentBased sampler from settings."""
    if not settings.TRACING_ENABLED:
        return ALWAYS_OFF
    rate = settings.TRACING_SAMPLE_RATE
    if rate >= 0.999:
        root = ALWAYS_ON
    elif rate <= 0.001:
        root = ALWAYS_OFF
    else:
        root = TraceIdRatioBased(rate)
    return ParentBased(root=root)


def _make_provider(*, role: str) -> TracerProvider:
    """Construct a TracerProvider with the right resource + sampler."""
    resource = Resource.create(
        {
            "service.name": settings.APP_NAME,
            "service.version": settings.APP_VERSION,
            "service.environment": settings.ENVIRONMENT,
            "service.role": role,  # "api" | "worker"
        }
    )
    provider = TracerProvider(resource=resource, sampler=_build_sampler())
    exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    return provider


def _install_provider(provider: TracerProvider) -> None:
    """Install the global TracerProvider and refresh module-level tracer."""
    global _tracer
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("scratch")


def _instrument_sqlalchemy() -> None:
    """Wrap SQLAlchemy engines so every query becomes a span."""
    engines_async = [main_engine, users_engine]
    if knowledge_engine:
        engines_async.append(knowledge_engine)
    # SQLAlchemyInstrumentor works against the underlying sync engine.
    engines = [
        e.sync_engine if isinstance(e, AsyncEngine) else e for e in engines_async
    ]
    SQLAlchemyInstrumentor().instrument(engines=engines)


def init_tracing(app: FastAPI) -> None:
    """Configure tracing for the FastAPI process."""
    if not settings.TRACING_ENABLED:
        # We still install a no-op provider so callers can use get_tracer()
        # without conditionals — they'll just get no-op spans.
        return

    provider = _make_provider(role="api")
    _install_provider(provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    _instrument_sqlalchemy()
    RedisInstrumentor().instrument()
    # CeleryInstrumentor attaches *outgoing* span context to messages the
    # API process publishes (task.delay). Worker-side instrumentation is
    # done in init_tracing_for_worker().
    CeleryInstrumentor().instrument()


def init_tracing_for_worker() -> None:
    """Configure tracing inside a Celery worker process.

    Celery forks workers from the master — each worker is a fresh
    process and must re-initialize the OpenTelemetry SDK. We hook this
    into ``worker_process_init`` in celery_app.py.
    """
    if not settings.TRACING_ENABLED:
        return

    provider = _make_provider(role="worker")
    _install_provider(provider)

    _instrument_sqlalchemy()
    RedisInstrumentor().instrument()
    # Picks up the parent context attached by the API and creates a
    # `run` span per executed task.
    CeleryInstrumentor().instrument()
