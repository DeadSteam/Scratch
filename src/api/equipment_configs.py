"""Equipment configuration endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from ..core.dependencies import CurrentAdmin, EquipmentConfigSvc, MainDBSession
from ..schemas.equipment_config import (
    EquipmentConfigCreate,
    EquipmentConfigRead,
    EquipmentConfigUpdate,
)
from .responses import PaginatedResponse, Response

router = APIRouter(prefix="/equipment-configs", tags=["Equipment Configurations"])


@router.get(
    "/",
    response_model=PaginatedResponse[EquipmentConfigRead],
    summary="List equipment configurations",
    description="Get paginated list of all equipment configurations",
)
async def list_configs(
    config_service: EquipmentConfigSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
):
    """Get list of equipment configurations."""
    configs = await config_service.get_all(db, skip, limit)
    total = await config_service.count(db)

    return PaginatedResponse(
        success=True,
        data=configs,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(configs)) < total,
    )


@router.get(
    "/search",
    response_model=PaginatedResponse[EquipmentConfigRead],
    summary="Search configs by name",
    description="Search equipment configurations by name pattern",
)
async def search_configs(
    config_service: EquipmentConfigSvc,
    db: MainDBSession,
    name: str = Query(..., min_length=1, description="Name pattern to search for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Search equipment configurations by name."""
    configs = await config_service.search_by_name(name, db, skip, limit)

    return PaginatedResponse(
        success=True,
        data=configs,
        total=len(configs),
        skip=skip,
        limit=limit,
        has_more=len(configs) == limit,
    )


@router.get(
    "/head-type/{head_type}",
    response_model=PaginatedResponse[EquipmentConfigRead],
    summary="Get configs by head type",
    description="Get all configurations for a specific head type",
)
async def get_configs_by_head_type(
    head_type: str,
    config_service: EquipmentConfigSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get configurations by head type."""
    configs = await config_service.get_by_head_type(head_type, db, skip, limit)

    return PaginatedResponse(
        success=True,
        data=configs,
        total=len(configs),
        skip=skip,
        limit=limit,
        has_more=len(configs) == limit,
    )


@router.get(
    "/{config_id}",
    response_model=Response[EquipmentConfigRead],
    summary="Get config by ID",
    description="Retrieve a specific equipment configuration by ID",
)
async def get_config(
    config_id: UUID, config_service: EquipmentConfigSvc, db: MainDBSession
):
    """Get equipment configuration by ID."""
    config = await config_service.get_by_id(config_id, db)
    return Response(
        success=True,
        message="Equipment configuration retrieved successfully",
        data=config,
    )


@router.post(
    "/",
    response_model=Response[EquipmentConfigRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create equipment config",
    description="Create a new equipment configuration",
)
async def create_config(
    config_data: EquipmentConfigCreate,
    config_service: EquipmentConfigSvc,
    db: MainDBSession,
    admin: CurrentAdmin,
):
    """Create a new equipment configuration."""
    config = await config_service.create(config_data, db)
    return Response(
        success=True,
        message="Equipment configuration created successfully",
        data=config,
    )


@router.patch(
    "/{config_id}",
    response_model=Response[EquipmentConfigRead],
    summary="Update equipment config",
    description="Update equipment configuration information",
)
async def update_config(
    config_id: UUID,
    config_data: EquipmentConfigUpdate,
    config_service: EquipmentConfigSvc,
    db: MainDBSession,
    admin: CurrentAdmin,
):
    """Update equipment configuration."""
    config = await config_service.update(config_id, config_data, db)
    return Response(
        success=True,
        message="Equipment configuration updated successfully",
        data=config,
    )


@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete equipment config",
    description="Permanently delete an equipment configuration",
)
async def delete_config(
    config_id: UUID, config_service: EquipmentConfigSvc, db: MainDBSession, admin: CurrentAdmin
):
    """Delete equipment configuration."""
    await config_service.delete(config_id, db)
    return None
