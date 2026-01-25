"""Experiment management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from ..core.dependencies import ExperimentSvc, MainDBSession
from ..schemas.experiment import ExperimentCreate, ExperimentRead, ExperimentUpdate
from .responses import PaginatedResponse, Response

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get(
    "/",
    response_model=PaginatedResponse[ExperimentRead],
    summary="List experiments",
    description="Get paginated list of all experiments",
)
async def list_experiments(
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
):
    """Get list of experiments with pagination."""
    experiments = await experiment_service.get_all(db, skip, limit)

    return PaginatedResponse(
        success=True,
        data=experiments,
        total=len(experiments),
        skip=skip,
        limit=limit,
        has_more=len(experiments) == limit,
    )


@router.get(
    "/user/{user_id}",
    response_model=PaginatedResponse[ExperimentRead],
    summary="Get experiments by user",
    description="Get all experiments conducted by a specific user",
)
async def get_experiments_by_user(
    user_id: UUID,
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get experiments by user ID."""
    experiments = await experiment_service.get_by_user_id(user_id, db, skip, limit)

    return PaginatedResponse(
        success=True,
        data=experiments,
        total=len(experiments),
        skip=skip,
        limit=limit,
        has_more=len(experiments) == limit,
    )


@router.get(
    "/film/{film_id}",
    response_model=PaginatedResponse[ExperimentRead],
    summary="Get experiments by film",
    description="Get all experiments using a specific film",
)
async def get_experiments_by_film(
    film_id: UUID,
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get experiments by film ID."""
    experiments = await experiment_service.get_by_film_id(film_id, db, skip, limit)

    return PaginatedResponse(
        success=True,
        data=experiments,
        total=len(experiments),
        skip=skip,
        limit=limit,
        has_more=len(experiments) == limit,
    )


@router.get(
    "/config/{config_id}",
    response_model=PaginatedResponse[ExperimentRead],
    summary="Get experiments by config",
    description="Get all experiments using a specific equipment configuration",
)
async def get_experiments_by_config(
    config_id: UUID,
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get experiments by equipment config ID."""
    experiments = await experiment_service.get_by_config_id(config_id, db, skip, limit)

    return PaginatedResponse(
        success=True,
        data=experiments,
        total=len(experiments),
        skip=skip,
        limit=limit,
        has_more=len(experiments) == limit,
    )


@router.post(
    "/",
    response_model=Response[ExperimentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create experiment",
    description="Create a new experiment",
)
async def create_experiment(
    experiment_data: ExperimentCreate, experiment_service: ExperimentSvc, db: MainDBSession
):
    """Create a new experiment."""
    experiment = await experiment_service.create(experiment_data, db)
    return Response(success=True, message="Experiment created successfully", data=experiment)


@router.get(
    "/{experiment_id}",
    response_model=Response[ExperimentRead],
    summary="Get experiment by ID",
    description="Retrieve a specific experiment by its ID",
)
async def get_experiment(experiment_id: UUID, experiment_service: ExperimentSvc, db: MainDBSession):
    """Get experiment by ID."""
    experiment = await experiment_service.get_by_id(experiment_id, db)
    return Response(success=True, message="Experiment retrieved successfully", data=experiment)


@router.get(
    "/{experiment_id}/with-images",
    response_model=Response[ExperimentRead],
    summary="Get experiment with images",
    description="Retrieve experiment with all related images",
)
async def get_experiment_with_images(
    experiment_id: UUID, experiment_service: ExperimentSvc, db: MainDBSession
):
    """Get experiment with all related images."""
    experiment = await experiment_service.get_with_images(experiment_id, db)
    return Response(
        success=True, message="Experiment with images retrieved successfully", data=experiment
    )


@router.patch(
    "/{experiment_id}",
    response_model=Response[ExperimentRead],
    summary="Update experiment",
    description="Update experiment information",
)
async def update_experiment(
    experiment_id: UUID,
    experiment_data: ExperimentUpdate,
    experiment_service: ExperimentSvc,
    db: MainDBSession,
):
    """Update experiment information."""
    experiment = await experiment_service.update(experiment_id, experiment_data, db)
    return Response(success=True, message="Experiment updated successfully", data=experiment)


@router.delete(
    "/{experiment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete experiment",
    description="Permanently delete an experiment",
)
async def delete_experiment(
    experiment_id: UUID, experiment_service: ExperimentSvc, db: MainDBSession
):
    """Delete experiment."""
    await experiment_service.delete(experiment_id, db)
    return None
