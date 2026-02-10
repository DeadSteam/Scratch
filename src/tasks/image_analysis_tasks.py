"""Background tasks for image analysis.

Incremental architecture: each image is analyzed individually and its
scratch index is appended to the experiment's scratch_results array.
Full recalculation is available when ROI changes.
"""

from __future__ import annotations

from typing import Any

from ..core.celery_app import celery_app
from ..core.logging_config import get_logger
from ..repositories.experiment_repository import ExperimentRepository
from ..repositories.image_repository import ExperimentImageRepository
from ..services.image_analysis_service import ImageAnalysisService
from .helpers import run_async

logger = get_logger("tasks.image_analysis")

_image_repo = ExperimentImageRepository()
_experiment_repo = ExperimentRepository()
_analysis_service = ImageAnalysisService(_image_repo, _experiment_repo)


@celery_app.task(
    name="src.tasks.image_analysis_tasks.analyze_single_image",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def analyze_single_image(
    self: Any,
    image_id: str,
) -> dict[str, Any]:
    """Analyze ONE image and append to scratch_results (incremental).

    This is the primary task — called after uploading a new image.
    """
    from uuid import UUID

    logger.info(
        "single_image_task_started",
        task_id=self.request.id,
        image_id=image_id,
    )
    try:
        result = run_async(_analyze_single(UUID(image_id)))
        logger.info(
            "single_image_task_completed",
            task_id=self.request.id,
            image_id=image_id,
        )
        return result
    except Exception as exc:
        logger.error(
            "single_image_task_failed",
            task_id=self.request.id,
            image_id=image_id,
            error=str(exc),
        )
        raise self.retry(exc=exc) from exc


@celery_app.task(
    name="src.tasks.image_analysis_tasks.recalculate_experiment",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
)
def recalculate_experiment(
    self: Any,
    experiment_id: str,
) -> dict[str, Any]:
    """Full recalculation of ALL images in an experiment.

    Use when ROI (rect_coords) changes.
    """
    from uuid import UUID

    logger.info(
        "recalculate_task_started",
        task_id=self.request.id,
        experiment_id=experiment_id,
    )
    try:
        result = run_async(
            _recalculate_experiment(UUID(experiment_id))
        )
        logger.info(
            "recalculate_task_completed",
            task_id=self.request.id,
            experiment_id=experiment_id,
        )
        return result
    except Exception as exc:
        logger.error(
            "recalculate_task_failed",
            task_id=self.request.id,
            experiment_id=experiment_id,
            error=str(exc),
        )
        raise self.retry(exc=exc) from exc


# ---------------------------------------------------------------------------
# Async helpers
# ---------------------------------------------------------------------------
async def _analyze_single(image_id: Any) -> dict[str, Any]:
    from ..core.database import MainSessionLocal

    async with MainSessionLocal() as session:
        try:
            result = await _analysis_service.analyze_and_save_single(
                image_id, session
            )
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise


async def _recalculate_experiment(
    experiment_id: Any,
) -> dict[str, Any]:
    from ..core.database import MainSessionLocal

    async with MainSessionLocal() as session:
        try:
            result = await _analysis_service.recalculate_experiment(
                experiment_id, session
            )
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
