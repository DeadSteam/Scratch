from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .api import api_router
from .api.errors import service_exception_handler, validation_exception_handler
from .core.config import settings
from .core.database import close_db_connections, get_users_db_session
from .core.init_data import initialize_default_data
from .core.logging_config import configure_logging, get_logger
from .core.metrics import init_metrics, record_exception
from .core.middleware import register_middlewares
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
    logger.info("Starting up application...")

    # Initialize default data (admin user, etc.)
    try:
        async for session in get_users_db_session():
            await initialize_default_data(session)
            break  # Only need one session
    except Exception as e:
        logger.error(f"Failed to initialize default data: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application...")
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

# OpenTelemetry tracing
init_tracing(app)

# Expose Prometheus metrics
init_metrics(app)

# Add exception handlers
app.add_exception_handler(ServiceError, service_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler that ensures CORS headers are present."""
    record_exception()
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=str(request.url.path),
        exc_info=True,
    )

    # Create error response
    error_response = {
        "message": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An internal error occurred",
    }

    # Create JSONResponse with CORS headers
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response
    )

    # Add CORS headers manually
    origin = request.headers.get("origin")
    if origin and origin in settings.CORS_ORIGINS:
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


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
