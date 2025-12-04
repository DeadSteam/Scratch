"""Experiment image service."""
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from .exceptions import NotFoundError, ValidationError as ServiceValidationError
from ..repositories.image_repository import ExperimentImageRepository
from ..repositories.experiment_repository import ExperimentRepository
from ..schemas.image import ExperimentImageCreate, ExperimentImageUpdate, ExperimentImageRead
from ..models.image import ExperimentImage


class ExperimentImageService(BaseService[ExperimentImage, ExperimentImageCreate, ExperimentImageUpdate, ExperimentImageRead]):
    """Experiment image service."""
    
    def __init__(
        self,
        repository: ExperimentImageRepository,
        experiment_repository: ExperimentRepository,
    ):
        super().__init__(
            repository=repository,
            entity_name="ExperimentImage",
            create_schema=ExperimentImageCreate,
            update_schema=ExperimentImageUpdate,
            read_schema=ExperimentImageRead,
        )
        self.image_repo = repository
        self.experiment_repo = experiment_repository
    
    async def create(
        self,
        data: ExperimentImageCreate,
        session: AsyncSession
    ) -> ExperimentImageRead:
        """Create image with experiment validation."""
        # Validate experiment exists
        if not await self.experiment_repo.exists(data.experiment_id, session):
            raise NotFoundError("Experiment", data.experiment_id)
        
        return await super().create(data, session)
    
    async def get_by_experiment_id(
        self,
        experiment_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExperimentImageRead]:
        """Get all images for an experiment."""
        # Validate experiment exists
        if not await self.experiment_repo.exists(experiment_id, session):
            raise NotFoundError("Experiment", experiment_id)
        
        images = await self.image_repo.get_by_experiment_id(experiment_id, session, skip, limit)
        return [self.read_schema.model_validate(img) for img in images]
    
    async def delete_by_experiment_id(
        self,
        experiment_id: UUID,
        session: AsyncSession
    ) -> int:
        """Delete all images for an experiment."""
        # Validate experiment exists
        if not await self.experiment_repo.exists(experiment_id, session):
            raise NotFoundError("Experiment", experiment_id)
        
        return await self.image_repo.delete_by_experiment_id(experiment_id, session)
    
    async def get_raw_by_id(
        self,
        entity_id: UUID,
        session: AsyncSession
    ) -> ExperimentImage:
        """Get raw image model with binary data."""
        entity = await self.repository.get_by_id(entity_id, session)
        if not entity:
            raise NotFoundError(self.entity_name, entity_id)
        return entity












