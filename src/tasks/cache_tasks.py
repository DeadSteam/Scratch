"""Background tasks for cache management.

Periodic and on-demand cache warming / invalidation.
"""

from __future__ import annotations

from typing import Any

from ..core.celery_app import celery_app
from ..core.logging_config import get_logger
from .helpers import run_async

logger = get_logger("tasks.cache")


@celery_app.task(
    name="src.tasks.cache_tasks.warm_cache",
    bind=True,
    max_retries=1,
    default_retry_delay=60,
)
def warm_cache(self: Any) -> dict[str, Any]:
    """Pre-populate frequently accessed cache entries.

    Runs periodically via Celery Beat (see celery_app.py schedule).
    """
    logger.info("cache_warm_started", task_id=self.request.id)

    try:
        stats = run_async(_warm_cache_impl())
        logger.info(
            "cache_warm_completed",
            task_id=self.request.id,
            **stats,
        )
        return stats
    except Exception as exc:
        logger.error(
            "cache_warm_failed",
            task_id=self.request.id,
            error=str(exc),
        )
        raise self.retry(exc=exc) from exc


@celery_app.task(
    name="src.tasks.cache_tasks.invalidate_entity_cache",
)
def invalidate_entity_cache(entity_type: str, entity_id: str) -> bool:
    """Invalidate cache for a specific entity after mutation.

    Call after create / update / delete to keep cache consistent.
    """
    logger.info(
        "cache_invalidate",
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return run_async(_invalidate_impl(entity_type, entity_id))


# ---------------------------------------------------------------------------
# Async helpers
# ---------------------------------------------------------------------------
async def _warm_cache_impl() -> dict[str, Any]:
    """Warm cache for experiments and knowledge entries."""
    from ..core.database import KnowledgeSessionLocal, MainSessionLocal
    from ..core.redis import get_redis_client
    from ..repositories.experiment_repository import ExperimentRepository
    from ..repositories.situation_repository import SituationRepository

    client = await get_redis_client()
    warmed = 0

    # Warm experiment list (first page)
    exp_repo = ExperimentRepository()
    async with MainSessionLocal() as session:
        experiments = await exp_repo.get_all(session, skip=0, limit=50)
        for exp in experiments:
            key = f"experiment:{exp.id}"
            already = await client.exists(key)
            if not already:
                warmed += 1

    # Warm situation list (if knowledge DB configured)
    if KnowledgeSessionLocal is not None:
        sit_repo = SituationRepository()
        async with KnowledgeSessionLocal() as session:
            situations = await sit_repo.get_all(session, skip=0, limit=50)
            for sit in situations:
                key = f"situation:{sit.id}"
                already = await client.exists(key)
                if not already:
                    warmed += 1

    return {"warmed_entries": warmed}


async def _invalidate_impl(entity_type: str, entity_id: str) -> bool:
    from ..core.redis import get_redis_client

    client = await get_redis_client()
    pattern = f"{entity_type}:{entity_id}*"
    deleted = await client.delete_pattern(pattern)
    return deleted > 0
