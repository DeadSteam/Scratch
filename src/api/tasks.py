"""API endpoints for background task management.

- Submit incremental / recalculation tasks (returns task_id)
- Poll task status by task_id
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter

from ..api.responses import Response
from ..core.celery_app import celery_app
from ..core.dependencies import CurrentUser, MainDBSession
from ..repositories.experiment_repository import ExperimentRepository
from ..services.exceptions import NotFoundError

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ---------------------------------------------------------------------------
# Submit single-image analysis task
# ---------------------------------------------------------------------------
@router.post("/analyze-image/{image_id}")
async def submit_single_analysis(
    image_id: UUID,
    _current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Submit a single image for background analysis.

    The scratch index will be calculated and appended to the
    experiment's ``scratch_results`` array.
    """
    from ..tasks.image_analysis_tasks import analyze_single_image

    task = analyze_single_image.delay(str(image_id))
    return Response(
        success=True,
        message="Analysis task submitted",
        data={
            "task_id": task.id,
            "status": "PENDING",
            "image_id": str(image_id),
        },
    )


# ---------------------------------------------------------------------------
# Submit full experiment recalculation
# ---------------------------------------------------------------------------
@router.post("/recalculate-experiment/{experiment_id}")
async def submit_recalculation(
    experiment_id: UUID,
    db: MainDBSession,
    _current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Submit a full experiment recalculation.

    Recalculates scratch index for every image and overwrites
    ``scratch_results``.  Use when ROI changes.
    """
    from ..tasks.experiment_tasks import batch_analyze_and_save

    repo = ExperimentRepository()
    if not await repo.exists(experiment_id, db):
        raise NotFoundError("Experiment", experiment_id)

    task = batch_analyze_and_save.delay(str(experiment_id))
    return Response(
        success=True,
        message="Recalculation task submitted",
        data={
            "task_id": task.id,
            "status": "PENDING",
            "experiment_id": str(experiment_id),
        },
    )


# ---------------------------------------------------------------------------
# Poll task status
# ---------------------------------------------------------------------------
@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    _current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Get the status and result of a background task."""
    result = AsyncResult(task_id, app=celery_app)

    data: dict[str, Any] = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.ready():
        if result.successful():
            data["result"] = result.result
        else:
            data["error"] = str(result.result)

    return Response(
        success=True,
        message=f"Task status: {result.status}",
        data=data,
    )
