import logging
import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .api import api_router
from .api.errors import service_exception_handler, validation_exception_handler
from .core.config import settings
from .core.database import close_db_connections, get_users_db_session
from .core.init_data import initialize_default_data
from .core.redis import close_redis_connection
from .services.exceptions import ServiceException

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()), format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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

# Add exception handlers
app.add_exception_handler(ServiceException, service_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler that ensures CORS headers are present."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    logger.error(f"Traceback: {traceback.format_exc()}")

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


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

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
