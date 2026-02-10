"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .api import api_router
from .api.errors import service_exception_handler, validation_exception_handler
from .api.health import router as health_router
from .core.config import settings
from .core.database import close_db_connections, get_users_db_transaction
from .core.init_data import initialize_default_data
from .core.logging_config import configure_logging, get_logger
from .core.metrics import init_metrics, record_exception
from .core.middleware import register_middlewares
from .core.rate_limit import limiter
from .core.redis import close_redis_connection
from .core.tracing import init_tracing
from .services.exceptions import ServiceError

# Configure structured logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager."""
    # Startup
    logger.info("application_starting")

    # Initialize default data (admin user, etc.) in a single transaction
    try:
        async with get_users_db_transaction() as session:
            await initialize_default_data(session)
    except Exception:
        logger.exception("failed_to_initialize_default_data")

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_db_connections()
    await close_redis_connection()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# OpenTelemetry tracing
init_tracing(app)

# Expose Prometheus metrics
init_metrics(app)

# Add exception handlers
app.add_exception_handler(ServiceError, service_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Global exception handler that ensures CORS headers are present."""
    record_exception()
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=str(request.url.path),
        exc_info=True,
    )

    error_response = {
        "success": False,
        "message": "Internal server error",
        "detail": (
            str(exc) if settings.DEBUG else "An internal error occurred"
        ),
    }

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )

    # Add CORS headers manually for unhandled exceptions
    origin = request.headers.get("origin")
    if origin and (
        origin in settings.CORS_ORIGINS or "*" in settings.CORS_ORIGINS
    ):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = ", ".join(
            settings.CORS_METHODS
        )
        response.headers["Access-Control-Allow-Headers"] = ", ".join(
            settings.CORS_HEADERS
        )

    return response


# Register all middlewares in a single place
register_middlewares(app)

# Health / readiness / liveness (outside /api/v1 — must be reachable
# without auth by load balancers and orchestrators).
app.include_router(health_router)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to Experiment Management API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
