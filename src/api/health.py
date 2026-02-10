"""Health check endpoints with deep component verification."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from ..core.config import settings
from ..core.database import (
    KnowledgeSessionLocal,
    MainSessionLocal,
    UsersSessionLocal,
)
from ..core.logging_config import get_logger
from ..core.redis import get_redis_client

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


async def _check_db(
    name: str, session_factory: Any
) -> dict[str, Any]:
    """Ping a database and return component status."""
    start = time.monotonic()
    try:
        if session_factory is None:
            return {
                "status": "not_configured",
                "latency_ms": 0,
            }
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        latency = round((time.monotonic() - start) * 1000, 2)
        return {"status": "healthy", "latency_ms": latency}
    except Exception as exc:
        latency = round((time.monotonic() - start) * 1000, 2)
        logger.warning(
            "health_check_db_failed",
            db=name,
            error=str(exc),
        )
        return {
            "status": "unhealthy",
            "latency_ms": latency,
            "error": str(exc),
        }


async def _check_redis() -> dict[str, Any]:
    """Ping Redis and return component status."""
    start = time.monotonic()
    try:
        client = await get_redis_client()
        pong = await client.client.ping()
        latency = round((time.monotonic() - start) * 1000, 2)
        return {
            "status": "healthy" if pong else "unhealthy",
            "latency_ms": latency,
        }
    except Exception as exc:
        latency = round((time.monotonic() - start) * 1000, 2)
        logger.warning("health_check_redis_failed", error=str(exc))
        return {
            "status": "unhealthy",
            "latency_ms": latency,
            "error": str(exc),
        }


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Deep health check — verifies DB and Redis connectivity."""
    components: dict[str, dict[str, Any]] = {}

    # Check all databases in parallel-style (sequential but fast)
    components["experiments_db"] = await _check_db(
        "experiments", MainSessionLocal
    )
    components["users_db"] = await _check_db("users", UsersSessionLocal)
    components["knowledge_db"] = await _check_db(
        "knowledge", KnowledgeSessionLocal
    )
    components["redis"] = await _check_redis()

    # Overall status is healthy only if all configured components are ok
    overall = "healthy"
    for comp_status in components.values():
        if comp_status["status"] == "unhealthy":
            overall = "unhealthy"
            break

    return {
        "status": overall,
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "components": components,
    }


@router.get("/health/liveness")
async def liveness() -> dict[str, str]:
    """Kubernetes-style liveness probe (always OK if process runs)."""
    return {"status": "alive"}


@router.get("/health/readiness")
async def readiness() -> dict[str, Any]:
    """Kubernetes-style readiness probe (checks critical deps)."""
    db_status = await _check_db("experiments", MainSessionLocal)
    redis_status = await _check_redis()

    ready = (
        db_status["status"] == "healthy"
        and redis_status["status"] == "healthy"
    )
    return {
        "status": "ready" if ready else "not_ready",
        "experiments_db": db_status["status"],
        "redis": redis_status["status"],
    }
