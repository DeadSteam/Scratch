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
from ..core.authorization import ensure_experiment_access, ensure_image_access, is_admin
from ..core.celery_app import celery_app
from ..core.dependencies import CurrentUser, MainDBSession
from ..core.redis import get_redis_client
from ..schemas.user import UserRead
from ..services.exceptions import AuthorizationError

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Task ownership records let /tasks/{task_id} reject requests for tasks
# submitted by other users (IDOR). TTL mirrors Celery's result_expires so
# the ownership record and the task result expire together.
_TASK_OWNER_KEY_PREFIX = "task_owner"
_TASK_OWNER_TTL_SECONDS = 86400


async def _record_task_owner(task_id: str, user_id: UUID) -> None:
    """Remember which user submitted a background task."""
    redis = await get_redis_client()
    await redis.set(
        f"{_TASK_OWNER_KEY_PREFIX}:{task_id}",
        str(user_id),
        expire=_TASK_OWNER_TTL_SECONDS,
    )


async def _ensure_task_access(task_id: str, user: UserRead) -> None:
    """Verify the user submitted this task (or is an admin)."""
    if is_admin(user):
        return
    redis = await get_redis_client()
    owner_id = await redis.get(f"{_TASK_OWNER_KEY_PREFIX}:{task_id}")
    if owner_id != str(user.id):
        raise AuthorizationError("Access forbidden: you do not own this task")


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
    await _record_task_owner(task.id, current_user.id)
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
    await _record_task_owner(task.id, current_user.id)
    return Response(
        success=True,
        message="Recalculation task submitted",
        data={
            "task_id": task.id,
            "status": "PENDING",
            "experiment_id": str(experiment_id),
        },
    )


@router.post("/quick-analysis/{experiment_id}")
async def submit_quick_analysis(
    experiment_id: UUID,
    db: MainDBSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Response[dict[str, Any]]:
    """Run a quick per-image analysis as a background task (B9).

    Use when the experiment has more images than the inline endpoint's cap.
    """
    await ensure_experiment_access(experiment_id, current_user, db)
    from ..tasks.image_analysis_tasks import quick_experiment_analysis

    task = quick_experiment_analysis.delay(str(experiment_id), skip, limit)
    await _record_task_owner(task.id, current_user.id)
    return Response(
        success=True,
        message="Quick analysis task submitted",
        data={
            "task_id": task.id,
            "status": "PENDING",
            "experiment_id": str(experiment_id),
        },
    )


@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Get the status and result of a background task."""
    await _ensure_task_access(task_id, current_user)
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
