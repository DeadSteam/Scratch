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

# Read uploads in 1 MiB chunks so a malicious client can't OOM us
# by sending a huge body before the size check runs.
_UPLOAD_CHUNK = 1024 * 1024

router = APIRouter(prefix="/images", tags=["Experiment Images"])


async def _read_upload_with_limit(file: UploadFile) -> bytes:
    """Read an upload, aborting as soon as MAX_FILE_SIZE is exceeded.

    Reading entire UploadFile.read() loads the whole body into memory
    BEFORE we can check its size — that's a DoS vector. We stream instead.
    """
    max_size = settings.MAX_FILE_SIZE
    buf = bytearray()
    while True:
        chunk = await file.read(_UPLOAD_CHUNK)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max allowed: {max_size} bytes",
            )
    return bytes(buf)


def _validate_image_bytes(content: bytes) -> str:
    """Validate image size and format via Pillow. Returns the detected MIME."""
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
    return real_mime


def _sniff_mime_from_bytes(image_bytes: bytes) -> str:
    """Fallback: detect MIME from magic bytes. Used for rows that pre-date
    the `mime_type` column (B11)."""
    if len(image_bytes) >= 3 and image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if len(image_bytes) >= 8 and image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if len(image_bytes) >= 6 and image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if (
        len(image_bytes) >= 12
        and image_bytes[:4] == b"RIFF"
        and image_bytes[8:12] == b"WEBP"
    ):
        return "image/webp"
    return "image/png"


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

    image_bytes = bytes(image.image_data)
    # B11: prefer the stored MIME captured at upload; fall back to sniffing
    # only for rows that pre-date the `mime_type` column.
    content_type = getattr(image, "mime_type", None) or _sniff_mime_from_bytes(
        image_bytes
    )

    return FastAPIResponse(
        content=image_bytes,
        media_type=content_type,
        # SECURITY: must be `private` — shared caches (CDN, corporate proxies)
        # would otherwise serve images across users.
        headers={"Cache-Control": "private, max-age=3600"},
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
    content = await _read_upload_with_limit(file)
    mime_type = _validate_image_bytes(content)

    image_create = ExperimentImageCreate(
        experiment_id=experiment_id,
        image_data=content,
        passes=passes,
        mime_type=mime_type,
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
    detected_mime = _validate_image_bytes(bytes(image_data.image_data))
    if not image_data.mime_type:
        image_data.mime_type = detected_mime
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
