"""Experiment management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from ..core.dependencies import CurrentUser, ExperimentSvc, MainDBSession
from ..core.logging_config import get_logger
from ..schemas.experiment import ExperimentCreate, ExperimentRead, ExperimentUpdate
from .responses import PaginatedResponse, Response

router = APIRouter(prefix="/experiments", tags=["Experiments"])
logger = get_logger(__name__)


@router.get(
    "/",
    response_model=PaginatedResponse[ExperimentRead],
    summary="List experiments",
    description="Get paginated list of all experiments",
)
async def list_experiments(
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
):
    """Get list of experiments with pagination."""
    logger.info("list_experiments", user_id=str(current_user.id), skip=skip, limit=limit)
    experiments = await experiment_service.get_all(db, skip, limit)
    total = await experiment_service.count(db)
    logger.info("list_experiments_result", count=len(experiments), total=total)
    return PaginatedResponse(
        success=True,
        data=experiments,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(experiments)) < total,
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
    logger.info("get_experiments_by_user", user_id=str(user_id), skip=skip, limit=limit)
    experiments = await experiment_service.get_by_user_id(user_id, db, skip, limit)
    logger.info(
        "get_experiments_by_user_result",
        user_id=str(user_id),
        count=len(experiments),
    )
    total = await experiment_service.count_by_user_id(user_id, db)
    return PaginatedResponse(
        success=True,
        data=experiments,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(experiments)) < total,
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
    logger.info("get_experiments_by_film", film_id=str(film_id), skip=skip, limit=limit)
    experiments = await experiment_service.get_by_film_id(film_id, db, skip, limit)
    logger.info(
        "get_experiments_by_film_result",
        film_id=str(film_id),
        count=len(experiments),
    )
    total = await experiment_service.count_by_film_id(film_id, db)
    return PaginatedResponse(
        success=True,
        data=experiments,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(experiments)) < total,
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
    logger.info(
        "get_experiments_by_config", config_id=str(config_id), skip=skip, limit=limit
    )
    experiments = await experiment_service.get_by_config_id(config_id, db, skip, limit)
    logger.info(
        "get_experiments_by_config_result",
        config_id=str(config_id),
        count=len(experiments),
    )
    total = await experiment_service.count_by_config_id(config_id, db)
    return PaginatedResponse(
        success=True,
        data=experiments,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(experiments)) < total,
    )


@router.post(
    "/",
    response_model=Response[ExperimentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create experiment",
    description="Create a new experiment",
)
async def create_experiment(
    experiment_data: ExperimentCreate,
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    current_user: CurrentUser,
):
    """Create a new experiment."""
    logger.info("create_experiment_started", user_id=str(current_user.id))
    # Ensure experiment is created for the authenticated user
    experiment_data.user_id = current_user.id
    experiment = await experiment_service.create(experiment_data, db)
    logger.info("create_experiment_success", experiment_id=str(experiment.id))
    return Response(
        success=True, message="Experiment created successfully", data=experiment
    )


@router.get(
    "/{experiment_id}",
    response_model=Response[ExperimentRead],
    summary="Get experiment by ID",
    description="Retrieve a specific experiment by its ID",
)
async def get_experiment(
    experiment_id: UUID, experiment_service: ExperimentSvc, db: MainDBSession
):
    """Get experiment by ID."""
    logger.info("get_experiment", experiment_id=str(experiment_id))
    experiment = await experiment_service.get_by_id(experiment_id, db)
    logger.info("get_experiment_result", experiment_id=str(experiment_id))
    return Response(
        success=True, message="Experiment retrieved successfully", data=experiment
    )


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
    logger.info("get_experiment_with_images", experiment_id=str(experiment_id))
    experiment = await experiment_service.get_with_images(experiment_id, db)
    logger.info("get_experiment_with_images_result", experiment_id=str(experiment_id))
    return Response(
        success=True,
        message="Experiment with images retrieved successfully",
        data=experiment,
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
    logger.info("update_experiment_started", experiment_id=str(experiment_id))
    experiment = await experiment_service.update(experiment_id, experiment_data, db)
    logger.info("update_experiment_success", experiment_id=str(experiment_id))
    return Response(
        success=True, message="Experiment updated successfully", data=experiment
    )


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
    logger.info("delete_experiment_started", experiment_id=str(experiment_id))
    await experiment_service.delete(experiment_id, db)
    logger.info("delete_experiment_success", experiment_id=str(experiment_id))
    return None
