"""Image analysis endpoints for scratch resistance calculation."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..core.dependencies import ExperimentSvc, ImageAnalysisSvc, MainDBSession
from ..services.exceptions import ValidationError as ServiceValidationError
from .responses import Response

router = APIRouter(prefix="/analysis", tags=["Image Analysis"])


class ScratchAnalysisRequest(BaseModel):
    """Request model for scratch analysis."""

    experiment_id: UUID = Field(..., description="Experiment ID")
    reference_image_id: UUID = Field(
        ..., description="Reference (non-scratched) image ID"
    )
    scratched_image_ids: list[UUID] = Field(
        ..., min_length=1, description="List of scratched image IDs"
    )


class HistogramData(BaseModel):
    """Histogram data model."""

    brightness_level: int = Field(
        ..., ge=0, le=255, description="Brightness level (0-255)"
    )
    pixel_count: int = Field(
        ..., ge=0, description="Number of pixels at this brightness"
    )


class ImageAnalysisResult(BaseModel):
    """Single image analysis result."""

    grayscale_shape: tuple[int, int] = Field(
        ..., description="Grayscale image dimensions (H, W)"
    )
    total_pixels: int = Field(..., description="Total number of pixels")
    brightness_levels_count: int = Field(
        ..., description="Number of unique brightness levels"
    )


class ScratchedImageResult(BaseModel):
    """Result for a single scratched image."""

    image_id: str = Field(..., description="Image UUID")
    passes: int = Field(..., description="Number of scratching passes")
    analysis: ImageAnalysisResult = Field(..., description="Image analysis data")
    scratch_index: float = Field(..., description="Calculated scratch index")


class ScratchAnalysisSummary(BaseModel):
    """Summary statistics for scratch analysis."""

    average_scratch_index: float = Field(
        ..., description="Average scratch index across all images"
    )
    max_scratch_index: float = Field(..., description="Maximum scratch index")
    min_scratch_index: float = Field(..., description="Minimum scratch index")
    num_scratched_images: int = Field(
        ..., description="Number of analyzed scratched images"
    )


class ScratchAnalysisResponse(BaseModel):
    """Complete scratch analysis response."""

    experiment_id: str = Field(..., description="Experiment UUID")
    reference_image: dict[str, object] = Field(
        ..., description="Reference image analysis"
    )
    scratched_images: list[ScratchedImageResult] = Field(
        ..., description="Scratched images analysis"
    )
    summary: ScratchAnalysisSummary = Field(..., description="Summary statistics")


@router.post(
    "/scratch-resistance",
    response_model=Response[ScratchAnalysisResponse],
    summary="Analyze scratch resistance",
    description="""
    Analyze experiment images to calculate scratch resistance index.
    
    Algorithm:
    1. Convert images to grayscale using: Grayscale = 0.3*R + 0.59*G + 0.11*B
    2. Calculate histogram for each image
    3. For each brightness level q compute pixel count x_q
    4. Calculate scratch index using linear convolution: U(X) = Σ(w_q * x_q)
    
    The scratch index represents the degree of scratching, where:
    - Lower values = less scratching (better resistance)
    - Higher values = more scratching (worse resistance)
    
    Results are automatically saved to the experiment's analysis_results field.
    """,
)
async def analyze_scratch_resistance(
    request: ScratchAnalysisRequest,
    analysis_service: ImageAnalysisSvc,
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    save_to_experiment: bool = Query(True, description="Save results to experiment"),
):
    """
    Analyze scratch resistance of polymer film.

    Performs comprehensive analysis comparing reference (non-scratched) image
    with scratched images to calculate scratch resistance metrics.
    """
    result = await analysis_service.analyze_experiment_images(
        experiment_id=request.experiment_id,
        reference_image_id=request.reference_image_id,
        scratched_image_ids=request.scratched_image_ids,
        session=db,
    )

    # Save results to experiment if requested
    if save_to_experiment:
        # Extract only image_id and scratch_index for storage
        # Include reference image as well
        scratch_results = []

        # Add reference image result
        if "scratch_index" in result["reference_image"]:
            scratch_results.append(
                {
                    "image_id": result["reference_image"]["image_id"],
                    "scratch_index": result["reference_image"]["scratch_index"],
                }
            )

        # Add scratched images results
        scratch_results.extend(
            [
                {"image_id": img["image_id"], "scratch_index": img["scratch_index"]}
                for img in result["scratched_images"]
            ]
        )

        await experiment_service.save_scratch_results(
            experiment_id=request.experiment_id,
            scratch_results=scratch_results,
            session=db,
        )

    return Response(
        success=True,
        message="Scratch resistance analysis completed successfully",
        data=result,
    )


@router.get(
    "/histogram/{image_id}",
    response_model=Response[dict[str, Any]],
    summary="Get image histogram",
    description="Get brightness histogram for image (uses experiment ROI if available)",
)
async def get_image_histogram(
    image_id: UUID, analysis_service: ImageAnalysisSvc, db: MainDBSession
):
    """Get histogram data for a single image."""
    from ..repositories.experiment_repository import ExperimentRepository
    from ..repositories.image_repository import ExperimentImageRepository

    # Get image
    image_repo = ExperimentImageRepository()
    image = await image_repo.get_by_id(image_id, db)

    if not image:
        from ..services.exceptions import NotFoundError

        raise NotFoundError("ExperimentImage", image_id)

    # Get experiment to retrieve ROI coordinates
    experiment_repo = ExperimentRepository()
    experiment = await experiment_repo.get_by_id(image.experiment_id, db)
    rect_coords = (
        experiment.rect_coords
        if experiment and hasattr(experiment, "rect_coords")
        else None
    )

    # Analyze image with ROI cropping if coordinates are available.
    # If ROI is out of bounds for this image (e.g. old photo size), use full image.
    try:
        analysis = analysis_service.analyze_image(image.image_data, rect_coords)
    except ServiceValidationError:
        analysis = analysis_service.analyze_image(image.image_data, None)

    return Response(
        success=True,
        message="Image histogram retrieved successfully",
        data={
            "image_id": str(image_id),
            "histogram": analysis["histogram"],
            "statistics": {
                "dominant_brightness": analysis["dominant_brightness"],
                "average_brightness_ratio": analysis["average_brightness_ratio"],
                "weighted_average_brightness": analysis["weighted_average_brightness"],
                "total_pixels": analysis["total_pixels"],
            },
        },
    )


@router.get(
    "/experiment/{experiment_id}/quick-analysis",
    response_model=Response[dict[str, Any]],
    summary="Quick analysis of all experiment images",
    description="Analyze all experiment images (simple stats, uses ROI if available)",
)
async def quick_experiment_analysis(
    experiment_id: UUID,
    analysis_service: ImageAnalysisSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Quick analysis of all experiment images."""
    from ..repositories.experiment_repository import ExperimentRepository
    from ..repositories.image_repository import ExperimentImageRepository

    # Get experiment to retrieve ROI coordinates
    experiment_repo = ExperimentRepository()
    experiment = await experiment_repo.get_by_id(experiment_id, db)
    rect_coords = (
        experiment.rect_coords
        if experiment and hasattr(experiment, "rect_coords")
        else None
    )

    # Get all images for experiment
    image_repo = ExperimentImageRepository()
    images = await image_repo.get_by_experiment_id(experiment_id, db, skip, limit)

    if not images:
        return Response(
            success=True,
            message="No images found for this experiment",
            data={"experiment_id": str(experiment_id), "images": []},
        )

    # Analyze each image with ROI cropping if coordinates are available
    results = []
    for image in images:
        try:
            analysis = analysis_service.analyze_image(image.image_data, rect_coords)
        except ServiceValidationError:
            analysis = analysis_service.analyze_image(image.image_data, None)
        results.append(
            {
                "image_id": str(image.id),
                "passes": image.passes,
                "dominant_brightness": analysis["dominant_brightness"],
                "weighted_average_brightness": analysis["weighted_average_brightness"],
                "total_pixels": analysis["total_pixels"],
            }
        )

    return Response(
        success=True,
        message=f"Analyzed {len(results)} images",
        data={
            "experiment_id": str(experiment_id),
            "images": results,
            "count": len(results),
        },
    )
