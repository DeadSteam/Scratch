"""Background tasks for experiment processing.

Offloads batch operations (full recalculation, bulk analysis) to workers.
For single images, use ``image_analysis_tasks.analyze_single_image``.
"""

from __future__ import annotations

from typing import Any

from ..core.celery_app import celery_app
from ..core.logging_config import get_logger
from ..repositories.experiment_repository import ExperimentRepository
from ..repositories.image_repository import ExperimentImageRepository
from ..services.image_analysis_service import ImageAnalysisService
from .helpers import run_async

logger = get_logger("tasks.experiment")

_image_repo = ExperimentImageRepository()
_experiment_repo = ExperimentRepository()
_analysis_service = ImageAnalysisService(_image_repo, _experiment_repo)


@celery_app.task(
    name="src.tasks.experiment_tasks.batch_analyze_and_save",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
)
def batch_analyze_and_save(
    self: Any,
    experiment_id: str,
) -> dict[str, Any]:
    """Recalculate and persist scratch_results for an entire experiment.

    Equivalent to ``recalculate_experiment`` but structured as a Celery
    task with retries.  The API returns a task ID immediately.
    """
    from uuid import UUID

    logger.info(
        "batch_task_started",
        task_id=self.request.id,
        experiment_id=experiment_id,
    )
    try:
        result = run_async(
            _recalculate_and_persist(UUID(experiment_id))
        )
        logger.info(
            "batch_task_completed",
            task_id=self.request.id,
            experiment_id=experiment_id,
        )
        return result
    except Exception as exc:
        logger.error(
            "batch_task_failed",
            task_id=self.request.id,
            experiment_id=experiment_id,
            error=str(exc),
        )
        raise self.retry(exc=exc) from exc


async def _recalculate_and_persist(
    experiment_id: Any,
) -> dict[str, Any]:
    from ..core.database import MainSessionLocal

    async with MainSessionLocal() as session:
        try:
            result = await _analysis_service.recalculate_experiment(
                experiment_id, session
            )
            await session.commit()
            return {
                "experiment_id": str(experiment_id),
                "status": "completed",
                "summary": result["summary"],
                "scratch_results_saved": result["summary"]["count"],
            }
        except Exception:
            await session.rollback()
            raise
