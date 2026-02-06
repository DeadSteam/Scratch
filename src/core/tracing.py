from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import settings
from .database import knowledge_engine, main_engine, users_engine
from sqlalchemy.ext.asyncio import AsyncEngine


def init_tracing(app: FastAPI) -> None:
    """Configure OpenTelemetry tracing and instrument FastAPI/SQLAlchemy/Redis."""
    resource = Resource.create(
        {
            "service.name": settings.APP_NAME,
            "service.version": settings.APP_VERSION,
            "service.environment": settings.ENVIRONMENT,
        }
    )

    provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint="http://tempo:4317", insecure=True)
    span_processor = BatchSpanProcessor(span_exporter)
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    # FastAPI / Starlette
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

    # SQLAlchemy engines
    engines_async = [main_engine, users_engine]
    if knowledge_engine:
        engines_async.append(knowledge_engine)

    # SQLAlchemy instrumentation работает с синхронными Engine;
    # для AsyncEngine используем их sync_engine.
    engines = [
        e.sync_engine if isinstance(e, AsyncEngine) else e for e in engines_async
    ]
    SQLAlchemyInstrumentor().instrument(engines=engines)

    # Redis (aioredis is supported via redis instrumentation)
    RedisInstrumentor().instrument()
