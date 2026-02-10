"""Image analysis endpoints for scratch resistance calculation."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query

from ..core.dependencies import (
    CurrentUser,
    ImageAnalysisSvc,
    MainDBSession,
)
from .responses import Response

router = APIRouter(prefix="/analysis", tags=["Image Analysis"])


# ---------------------------------------------------------------------------
# Incremental: analyze a SINGLE image
# ---------------------------------------------------------------------------
@router.post(
    "/image/{image_id}",
    response_model=Response[dict[str, Any]],
    summary="Analyze a single image (incremental)",
    description=(
        "Calculate scratch index for ONE image and append the result "
        "to the experiment's scratch_results array.  If the image was "
        "already analyzed, its entry is replaced (idempotent).  "
        "This is the preferred way to analyze images — no need to "
        "recalculate the entire experiment."
    ),
)
async def analyze_single_image(
    image_id: UUID,
    analysis_service: ImageAnalysisSvc,
    db: MainDBSession,
    _current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Analyze one image and save its scratch index."""
    entry = await analysis_service.analyze_and_save_single(
        image_id, db
    )
    return Response(
        success=True,
        message="Image analyzed and saved",
        data=entry,
    )


# ---------------------------------------------------------------------------
# Full recalculation (when ROI changes)
# ---------------------------------------------------------------------------
@router.post(
    "/experiment/{experiment_id}/recalculate",
    response_model=Response[dict[str, Any]],
    summary="Recalculate ALL images in experiment",
    description=(
        "Recalculate scratch indices for every image in the "
        "experiment and overwrite scratch_results.  Use when "
        "rect_coords (ROI) changes or when a full audit is needed."
    ),
)
async def recalculate_experiment(
    experiment_id: UUID,
    analysis_service: ImageAnalysisSvc,
    db: MainDBSession,
    _current_user: CurrentUser,
) -> Response[dict[str, Any]]:
    """Full recalculation of all experiment images."""
    result = await analysis_service.recalculate_experiment(
        experiment_id, db
    )
    return Response(
        success=True,
        message=(
            f"Recalculated {result['summary']['count']} images"
        ),
        data=result,
    )


# ---------------------------------------------------------------------------
# Read-only helpers
# ---------------------------------------------------------------------------
@router.get(
    "/histogram/{image_id}",
    response_model=Response[dict[str, Any]],
    summary="Get image histogram",
)
async def get_image_histogram(
    image_id: UUID,
    analysis_service: ImageAnalysisSvc,
    db: MainDBSession,
):
    """Brightness histogram for a single image."""
    data = await analysis_service.get_image_histogram(image_id, db)
    return Response(
        success=True,
        message="Image histogram retrieved",
        data=data,
    )


@router.get(
    "/experiment/{experiment_id}/quick-analysis",
    response_model=Response[dict[str, Any]],
    summary="Quick analysis of experiment images",
)
async def quick_experiment_analysis(
    experiment_id: UUID,
    analysis_service: ImageAnalysisSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Quick per-image stats (no write)."""
    data = await analysis_service.quick_analysis(
        experiment_id, db, skip, limit
    )
    msg = (
        f"Analyzed {data['count']} images"
        if data["images"]
        else "No images found for this experiment"
    )
    return Response(success=True, message=msg, data=data)
