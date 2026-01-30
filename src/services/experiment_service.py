"""Experiment service with business logic."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.experiment import Experiment
from ..repositories.equipment_config_repository import EquipmentConfigRepository
from ..repositories.experiment_repository import ExperimentRepository
from ..repositories.film_repository import FilmRepository
from ..repositories.user_repository import UserRepository
from ..schemas.experiment import ExperimentCreate, ExperimentRead, ExperimentUpdate
from .base import BaseService
from .exceptions import NotFoundError


class ExperimentService(
    BaseService[Experiment, ExperimentCreate, ExperimentUpdate, ExperimentRead]
):
    """Experiment service with business validation."""

    def __init__(
        self,
        repository: ExperimentRepository,
        user_repository: UserRepository,
        film_repository: FilmRepository,
        config_repository: EquipmentConfigRepository,
    ):
        super().__init__(
            repository=repository,
            entity_name="Experiment",
            create_schema=ExperimentCreate,
            update_schema=ExperimentUpdate,
            read_schema=ExperimentRead,
        )
        self.experiment_repo = repository
        self.user_repo = user_repository
        self.film_repo = film_repository
        self.config_repo = config_repository

    async def get_by_id(self, entity_id: UUID, session: AsyncSession) -> ExperimentRead:
        """Get experiment by ID with relationships loaded."""
        experiment = await self.experiment_repo.get_by_id_with_relations(
            entity_id, session
        )
        if not experiment:
            raise NotFoundError(self.entity_name, entity_id)
        return self.read_schema.model_validate(experiment)

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ExperimentRead]:
        """Get all experiments with relationships loaded."""
        experiments = await self.experiment_repo.get_all_with_relations(
            session, skip, limit
        )
        return [self.read_schema.model_validate(e) for e in experiments]

    async def create(
        self, data: ExperimentCreate, session: AsyncSession
    ) -> ExperimentRead:
        """Create experiment with validation of foreign keys."""
        # User is in users_db; user_id is verified by JWT.

        # Validate film exists
        if not await self.film_repo.exists(data.film_id, session):
            raise NotFoundError("Film", data.film_id)

        # Validate equipment config exists
        if not await self.config_repo.exists(data.config_id, session):
            raise NotFoundError("EquipmentConfig", data.config_id)

        # Create experiment
        return await super().create(data, session)

    async def update(
        self, entity_id: UUID, data: ExperimentUpdate, session: AsyncSession
    ) -> ExperimentRead:
        """Update experiment with validation of foreign keys."""
        # User is in users_db; we don't validate user_id here.

        # Validate foreign keys if provided
        if data.film_id and not await self.film_repo.exists(data.film_id, session):
            raise NotFoundError("Film", data.film_id)

        if data.config_id and not await self.config_repo.exists(
            data.config_id, session
        ):
            raise NotFoundError("EquipmentConfig", data.config_id)

        # Check if entity exists
        if not await self.experiment_repo.exists(entity_id, session):
            raise NotFoundError(self.entity_name, entity_id)

        # Convert Pydantic model to dict, exclude unset fields
        entity_data = data.model_dump(exclude_unset=True)

        if not entity_data:
            # No fields to update, just return current entity with relations
            experiment = await self.experiment_repo.get_by_id_with_relations(
                entity_id, session
            )
            if not experiment:
                raise NotFoundError(self.entity_name, entity_id)
            return self.read_schema.model_validate(experiment)

        # Update entity
        await self.experiment_repo.update(entity_id, entity_data, session)

        # Re-fetch with relationships loaded
        experiment = await self.experiment_repo.get_by_id_with_relations(
            entity_id, session
        )
        if not experiment:
            raise NotFoundError(self.entity_name, entity_id)

        return self.read_schema.model_validate(experiment)

    async def get_by_user_id(
        self, user_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ExperimentRead]:
        """Get experiments by user ID."""
        # User is in users_db; if missing we just return [].
        try:
            experiments = await self.experiment_repo.get_by_user_id(
                user_id, session, skip, limit
            )
            # Convert to read schema; relations may be unloaded
            result = []
            for exp in experiments:
                try:
                    # Use from_attributes=True to handle SQLAlchemy models
                    exp_read = self.read_schema.model_validate(
                        exp, from_attributes=True
                    )
                    result.append(exp_read)
                except Exception as e:
                    # Log validation error but continue processing other experiments
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to validate experiment {exp.id}: {e}")
                    # Create a minimal read schema without related objects
                    result.append(
                        self.read_schema.model_validate(
                            {
                                "id": exp.id,
                                "film_id": exp.film_id,
                                "config_id": exp.config_id,
                                "user_id": exp.user_id,
                                "date": exp.date,
                                "rect_coords": exp.rect_coords,
                                "weight": exp.weight,
                                "has_fabric": exp.has_fabric,
                                "scratch_results": exp.scratch_results,
                            },
                            from_attributes=True,
                        )
                    )
            return result
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Error getting experiments by user_id {user_id}: {e}", exc_info=True
            )
            raise

    async def get_by_film_id(
        self, film_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ExperimentRead]:
        """Get experiments by film ID."""
        # Validate film exists
        if not await self.film_repo.exists(film_id, session):
            raise NotFoundError("Film", film_id)

        experiments = await self.experiment_repo.get_by_film_id(
            film_id, session, skip, limit
        )
        return [self.read_schema.model_validate(e) for e in experiments]

    async def get_by_config_id(
        self, config_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ExperimentRead]:
        """Get experiments by config ID."""
        # Validate config exists
        if not await self.config_repo.exists(config_id, session):
            raise NotFoundError("EquipmentConfig", config_id)

        experiments = await self.experiment_repo.get_by_config_id(
            config_id, session, skip, limit
        )
        return [self.read_schema.model_validate(e) for e in experiments]

    async def get_with_images(
        self, experiment_id: UUID, session: AsyncSession
    ) -> ExperimentRead:
        """Get experiment with all related images."""
        experiment = await self.experiment_repo.get_with_images(experiment_id, session)
        if not experiment:
            raise NotFoundError("Experiment", experiment_id)
        return self.read_schema.model_validate(experiment)

    async def save_scratch_results(
        self,
        experiment_id: UUID,
        scratch_results: list[dict[str, Any]],
        session: AsyncSession,
    ) -> ExperimentRead:
        """
        Save scratch analysis results to experiment.

        Args:
            experiment_id: Experiment UUID
            scratch_results: Array of results for each image
                [{"image_id": "uuid", "passes": 5, "scratch_index": 0.034, ...}, ...]
        """
        # Check if experiment exists
        if not await self.experiment_repo.exists(experiment_id, session):
            raise NotFoundError("Experiment", experiment_id)

        # Update experiment with scratch results
        await self.experiment_repo.update(
            experiment_id, {"scratch_results": scratch_results}, session
        )

        # Re-fetch with relationships loaded
        experiment = await self.experiment_repo.get_by_id_with_relations(
            experiment_id, session
        )
        if not experiment:
            raise NotFoundError("Experiment", experiment_id)

        return self.read_schema.model_validate(experiment)
