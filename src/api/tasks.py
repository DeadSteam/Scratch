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
from ..core.authorization import ensure_experiment_access, ensure_image_access
from ..core.celery_app import celery_app
from ..core.dependencies import CurrentUser, MainDBSession

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/analyze-image/{image_id}")
async def submit_single_analysis(
    image_id: UUID,
    db: MainDBSession,
    current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Submit a single image for background analysis."""
    await ensure_image_access(image_id, current_user, db)
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


@router.post("/recalculate-experiment/{experiment_id}")
async def submit_recalculation(
    experiment_id: UUID,
    db: MainDBSession,
    current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Submit a full experiment recalculation."""
    await ensure_experiment_access(experiment_id, current_user, db)
    from ..tasks.experiment_tasks import batch_analyze_and_save

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
