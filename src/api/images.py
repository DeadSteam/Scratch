"""Experiment image endpoints."""

import io
from typing import Any
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response as FastAPIResponse
from PIL import Image as PilImage
from PIL import UnidentifiedImageError

from ..core.authorization import ensure_experiment_access, ensure_image_access
from ..core.config import settings
from ..core.dependencies import CurrentUser, ExperimentImageSvc, MainDBSession
from ..core.rate_limit import limiter
from ..schemas.image import ExperimentImageCreate, ExperimentImageRead
from .responses import PaginatedResponse, Response

_PIL_FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}

router = APIRouter(prefix="/images", tags=["Experiment Images"])


def _validate_image_bytes(content: bytes) -> None:
    """Validate image size and format via Pillow."""
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max allowed: {settings.MAX_FILE_SIZE} bytes",
        )
    try:
        img = PilImage.open(io.BytesIO(content))
        real_mime = _PIL_FORMAT_TO_MIME.get(img.format)
    except UnidentifiedImageError:
        real_mime = None

    if not real_mime or real_mime not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Allowed formats: JPEG, PNG, WebP",
        )


@router.get(
    "/experiment/{experiment_id}",
    response_model=PaginatedResponse[ExperimentImageRead],
    summary="Get images by experiment",
    description="Get all images for a specific experiment",
)
async def get_images_by_experiment(
    experiment_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all images for an experiment."""
    await ensure_experiment_access(experiment_id, current_user, db)
    images = await image_service.get_by_experiment_id(experiment_id, db, skip, limit)
    total = await image_service.count_by_experiment_id(experiment_id, db)

    return PaginatedResponse(
        success=True,
        data=images,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(images)) < total,
    )


@router.get(
    "/{image_id}",
    response_model=Response[ExperimentImageRead],
    summary="Get image by ID",
    description="Retrieve a specific image by its ID",
)
async def get_image(
    image_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
):
    """Get image by ID."""
    await ensure_image_access(image_id, current_user, db)
    image = await image_service.get_by_id(image_id, db)
    return Response(success=True, message="Image retrieved successfully", data=image)


@router.get(
    "/{image_id}/data",
    summary="Get image binary data",
    description="Retrieve the actual image binary data",
)
async def get_image_data(
    image_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
):
    """Get image binary data for display."""
    await ensure_image_access(image_id, current_user, db)
    image = await image_service.get_raw_by_id(image_id, db)

    content_type = "image/png"
    image_bytes = bytes(image.image_data)

    if len(image_bytes) >= 3 and image_bytes[:3] == b"\xff\xd8\xff":
        content_type = "image/jpeg"
    elif len(image_bytes) >= 8 and image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        content_type = "image/png"
    elif len(image_bytes) >= 6 and image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        content_type = "image/gif"
    elif (
        len(image_bytes) >= 12
        and image_bytes[:4] == b"RIFF"
        and image_bytes[8:12] == b"WEBP"
    ):
        content_type = "image/webp"

    return FastAPIResponse(
        content=image_bytes,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.post(
    "/upload",
    response_model=Response[ExperimentImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="Upload experiment image",
    description="Upload a new experiment image",
)
@limiter.limit("20/minute")
async def upload_image(
    request: Request,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
    experiment_id: UUID = Query(..., description="Experiment ID"),
    passes: int = Query(
        0, ge=0, le=1000, description="Number of passes (0 for reference image)"
    ),
    file: UploadFile = File(..., description="Image file"),
):
    """Upload a new experiment image."""
    await ensure_experiment_access(experiment_id, current_user, db)
    content = await file.read()
    _validate_image_bytes(content)

    image_create = ExperimentImageCreate(
        experiment_id=experiment_id, image_data=content, passes=passes
    )
    image = await image_service.create(image_create, db)

    return Response(success=True, message="Image uploaded successfully", data=image)


@router.post(
    "/",
    response_model=Response[ExperimentImageRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create experiment image",
    description="Create a new experiment image from raw data",
)
@limiter.limit("20/minute")
async def create_image(
    request: Request,
    image_data: ExperimentImageCreate,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
):
    """Create a new experiment image."""
    await ensure_experiment_access(image_data.experiment_id, current_user, db)
    _validate_image_bytes(bytes(image_data.image_data))
    image = await image_service.create(image_data, db)
    return Response(success=True, message="Image created successfully", data=image)


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete image",
    description="Permanently delete an experiment image",
)
async def delete_image(
    image_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
):
    """Delete image."""
    await ensure_image_access(image_id, current_user, db)
    await image_service.delete(image_id, db)
    return None


@router.delete(
    "/experiment/{experiment_id}/all",
    response_model=Response[dict[str, Any]],
    summary="Delete all experiment images",
    description="Delete all images associated with an experiment",
)
async def delete_all_experiment_images(
    experiment_id: UUID,
    image_service: ExperimentImageSvc,
    db: MainDBSession,
    current_user: CurrentUser,
):
    """Delete all images for an experiment."""
    await ensure_experiment_access(experiment_id, current_user, db)
    count = await image_service.delete_by_experiment_id(experiment_id, db)
    return Response(
        success=True, message=f"Deleted {count} images", data={"deleted_count": count}
    )
