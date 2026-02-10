from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.engine import CursorResult
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
        """Delete all images for an experiment.

        No commit — managed by session dependency.
        """
        stmt = delete(ExperimentImage).where(
            ExperimentImage.experiment_id == experiment_id
        )
        result = await session.execute(stmt)
        return cast(CursorResult[Any], result).rowcount

    async def count_by_experiment_id(
        self, experiment_id: UUID, session: AsyncSession
    ) -> int:
        """Count images for an experiment."""

        result = await session.execute(
            select(func.count(ExperimentImage.id)).where(
                ExperimentImage.experiment_id == experiment_id
            )
        )
        return result.scalar() or 0
