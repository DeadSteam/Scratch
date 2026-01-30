from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.image import ExperimentImage
from .base import CachedRepositoryImpl


class ExperimentImageRepository(CachedRepositoryImpl[ExperimentImage]):
    """Experiment image repository implementation."""

    def __init__(self) -> None:
        super().__init__(ExperimentImage)

    async def get_by_experiment_id(
        self,
        experiment_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExperimentImage]:
        """Get images by experiment ID."""
        result = await session.execute(
            select(ExperimentImage)
            .where(ExperimentImage.experiment_id == experiment_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_by_experiment_id(
        self, experiment_id: UUID, session: AsyncSession
    ) -> int:
        """Delete all images for an experiment."""
        from sqlalchemy import delete

        stmt = delete(ExperimentImage).where(
            ExperimentImage.experiment_id == experiment_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
