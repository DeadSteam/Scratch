from typing import Any
from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.experiment import Experiment
from .base import CachedRepositoryImpl
from .interfaces import ExperimentRepositoryInterface


class ExperimentRepository(
    CachedRepositoryImpl[Experiment], ExperimentRepositoryInterface[Experiment]
):
    """Experiment repository implementation."""

    def __init__(self) -> None:
        super().__init__(Experiment)

    async def create(self, data: dict[str, Any], session: AsyncSession) -> Experiment:
        """Create experiment and load relationships."""
        stmt = insert(Experiment).values(**data).returning(Experiment.id)
        result = await session.execute(stmt)
        await session.commit()
        new_id = result.scalar_one()

        # Re-fetch with relationships loaded
        return await self.get_by_id_with_relations(new_id, session)

    async def get_by_id_with_relations(self, id: UUID, session: AsyncSession) -> Experiment | None:
        """Get experiment by ID with film and config relationships loaded."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .where(Experiment.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Experiment]:
        """Get experiments by user ID with relationships loaded."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .where(Experiment.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_film_id(
        self, film_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Experiment]:
        """Get experiments by film ID with relationships loaded."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .where(Experiment.film_id == film_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_config_id(
        self, config_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Experiment]:
        """Get experiments by config ID with relationships loaded."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .where(Experiment.config_id == config_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_images(self, id: UUID, session: AsyncSession) -> Experiment | None:
        """Get experiment with related images, film, and config."""
        result = await session.execute(
            select(Experiment)
            .options(
                selectinload(Experiment.images),
                selectinload(Experiment.film),
                selectinload(Experiment.config),
            )
            .where(Experiment.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_with_relations(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Experiment]:
        """Get all experiments with relationships loaded."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user_id_cached(
        self, user_id: UUID, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Experiment]:
        """Get experiments by user ID with cache check."""
        redis_client = await self._get_redis_client()
        cache_key = f"experiment:user_id:{user_id}:skip:{skip}:limit:{limit}"

        # Try cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Experiment(**item) for item in cached_data]

        # Get from database
        experiments = await self.get_by_user_id(user_id, session, skip, limit)
        if experiments:
            # Cache the experiments
            experiments_dict = [
                {c.name: getattr(exp, c.name) for c in exp.__table__.columns} for exp in experiments
            ]
            await redis_client.set(cache_key, experiments_dict)

        return experiments
