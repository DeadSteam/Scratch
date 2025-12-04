"""Experiment image endpoints."""
from uuid import UUID
from fastapi import APIRouter, Query, status, UploadFile, File
from fastapi.responses import Response as FastAPIResponse

from ..core.dependencies import ExperimentImageSvc, MainDBSession
from ..schemas.image import ExperimentImageCreate, ExperimentImageRead
from .responses import Response, PaginatedResponse

router = APIRouter(prefix="/images", tags=["Experiment Images"])


@router.get(
    "/experiment/{experiment_id}",
    response_model=PaginatedResponse[ExperimentImageRead],
    summary="Get images by experiment",
    description="Get all images for a specific experiment"
)
async def get_images_by_experiment(
    experiment_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all images for an experiment."""
    images = await image_service.get_by_experiment_id(experiment_id, db, skip, limit)
    
    return PaginatedResponse(
        data=images,
        total=len(images),
        skip=skip,
        limit=limit,
        has_more=len(images) == limit
    )


@router.get(
    "/{image_id}",
    response_model=Response[ExperimentImageRead],
    summary="Get image by ID",
    description="Retrieve a specific image by its ID"
)
async def get_image(
    image_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession
):
    """Get image by ID."""
    image = await image_service.get_by_id(image_id, db)
    return Response(
        success=True,
        message="Image retrieved successfully",
        data=image
    )


@router.get(
    "/{image_id}/data",
    summary="Get image binary data",
    description="Retrieve the actual image binary data"
)
async def get_image_data(
    image_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession
):
    """Get image binary data for display."""
    # Get raw model with image_data
    image = await image_service.get_raw_by_id(image_id, db)
    
    # Detect content type from image data
    content_type = "image/png"
    image_bytes = bytes(image.image_data)
    
    if len(image_bytes) >= 3 and image_bytes[:3] == b'\xff\xd8\xff':
        content_type = "image/jpeg"
    elif len(image_bytes) >= 8 and image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        content_type = "image/png"
    elif len(image_bytes) >= 6 and image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        content_type = "image/gif"
    elif len(image_bytes) >= 12 and image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        content_type = "image/webp"
    
    return FastAPIResponse(
        content=image_bytes,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"}
    )


@router.post(
    "/upload",
    response_model=Response[ExperimentImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="Upload experiment image",
    description="Upload a new experiment image"
)
async def upload_image(
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    experiment_id: UUID = Query(..., description="Experiment ID"),
    passes: int = Query(0, ge=0, le=1000, description="Number of passes (0 for reference image)"),
    file: UploadFile = File(..., description="Image file"),
):
    """Upload a new experiment image."""
    # Read file content
    image_data = await file.read()
    
    # Create image
    image_create = ExperimentImageCreate(
        experiment_id=experiment_id,
        image_data=image_data,
        passes=passes
    )
    
    image = await image_service.create(image_create, db)
    
    return Response(
        success=True,
        message="Image uploaded successfully",
        data=image
    )


@router.post(
    "/",
    response_model=Response[ExperimentImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create experiment image",
    description="Create a new experiment image from raw data"
)
async def create_image(
    image_data: ExperimentImageCreate,
    image_service: ExperimentImageSvc,
    db: MainDBSession
):
    """Create a new experiment image."""
    image = await image_service.create(image_data, db)
    return Response(
        success=True,
        message="Image created successfully",
        data=image
    )


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete image",
    description="Permanently delete an experiment image"
)
async def delete_image(
    image_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession
):
    """Delete image."""
    await image_service.delete(image_id, db)
    return None


@router.delete(
    "/experiment/{experiment_id}/all",
    response_model=Response[dict],
    summary="Delete all experiment images",
    description="Delete all images associated with an experiment"
)
async def delete_all_experiment_images(
    experiment_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession
):
    """Delete all images for an experiment."""
    count = await image_service.delete_by_experiment_id(experiment_id, db)
    return Response(
        success=True,
        message=f"Deleted {count} images",
        data={"deleted_count": count}
    )

