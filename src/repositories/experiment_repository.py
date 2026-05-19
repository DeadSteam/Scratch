from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import CursorResult
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
        """Create experiment and load relationships.

        No commit — managed by session dependency.
        """
        stmt = insert(Experiment).values(**data).returning(Experiment.id)
        result = await session.execute(stmt)
        new_id = result.scalar_one()

        # Flush to ensure the INSERT is visible for the relationship query
        await session.flush()

        # Re-fetch with relationships loaded
        exp = await self.get_by_id_with_relations(new_id, session)
        if exp is None:
            raise RuntimeError("Created experiment not found")

        # Invalidate cache after successful creation
        await self.invalidate_cache()
        return exp

    async def get_by_id_with_relations(
        self, id: UUID, session: AsyncSession
    ) -> Experiment | None:
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

    async def get_with_images(
        self, id: UUID, session: AsyncSession
    ) -> Experiment | None:
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
        """Get experiments by user ID - always load with relationships."""
        # Always load from database with relationships to ensure film and
        # config are included. Caching experiments with relationships is
        # complex, so we skip cache for this query
        return await self.get_by_user_id(user_id, session, skip, limit)

    async def count_by_user_id(self, user_id: UUID, session: AsyncSession) -> int:
        """Count experiments by user ID."""
        result = await session.execute(
            select(func.count(Experiment.id)).where(Experiment.user_id == user_id)
        )
        return result.scalar() or 0

    async def count_by_film_id(self, film_id: UUID, session: AsyncSession) -> int:
        """Count experiments by film ID."""
        result = await session.execute(
            select(func.count(Experiment.id)).where(Experiment.film_id == film_id)
        )
        return result.scalar() or 0

    async def count_by_config_id(self, config_id: UUID, session: AsyncSession) -> int:
        """Count experiments by config ID."""
        result = await session.execute(
            select(func.count(Experiment.id)).where(Experiment.config_id == config_id)
        )
        return result.scalar() or 0

    async def get_by_film_id_for_user(
        self,
        film_id: UUID,
        user_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Experiment]:
        """Get experiments by film ID scoped to a user."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .where(Experiment.film_id == film_id, Experiment.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_config_id_for_user(
        self,
        config_id: UUID,
        user_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Experiment]:
        """Get experiments by config ID scoped to a user."""
        result = await session.execute(
            select(Experiment)
            .options(selectinload(Experiment.film), selectinload(Experiment.config))
            .where(
                Experiment.config_id == config_id,
                Experiment.user_id == user_id,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_film_id_for_user(
        self, film_id: UUID, user_id: UUID, session: AsyncSession
    ) -> int:
        """Count experiments by film ID scoped to a user."""
        result = await session.execute(
            select(func.count(Experiment.id)).where(
                Experiment.film_id == film_id,
                Experiment.user_id == user_id,
            )
        )
        return result.scalar() or 0

    async def count_by_config_id_for_user(
        self, config_id: UUID, user_id: UUID, session: AsyncSession
    ) -> int:
        """Count experiments by config ID scoped to a user."""
        result = await session.execute(
            select(func.count(Experiment.id)).where(
                Experiment.config_id == config_id,
                Experiment.user_id == user_id,
            )
        )
        return result.scalar() or 0

    # -----------------------------------------------------------------
    # B3: unified list/count. The legacy get_by_X / count_by_X / *_for_user
    # methods above remain as thin facades for back-compat.
    # -----------------------------------------------------------------
    async def list_experiments(
        self,
        session: AsyncSession,
        *,
        user_id: UUID | None = None,
        film_id: UUID | None = None,
        config_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Experiment]:
        """List experiments with optional filters."""
        stmt = select(Experiment).options(
            selectinload(Experiment.film), selectinload(Experiment.config)
        )
        if user_id is not None:
            stmt = stmt.where(Experiment.user_id == user_id)
        if film_id is not None:
            stmt = stmt.where(Experiment.film_id == film_id)
        if config_id is not None:
            stmt = stmt.where(Experiment.config_id == config_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def count_experiments(
        self,
        session: AsyncSession,
        *,
        user_id: UUID | None = None,
        film_id: UUID | None = None,
        config_id: UUID | None = None,
    ) -> int:
        """Count experiments with optional filters."""
        stmt = select(func.count(Experiment.id))
        if user_id is not None:
            stmt = stmt.where(Experiment.user_id == user_id)
        if film_id is not None:
            stmt = stmt.where(Experiment.film_id == film_id)
        if config_id is not None:
            stmt = stmt.where(Experiment.config_id == config_id)
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def delete_by_user_id(
        self, user_id: UUID, session: AsyncSession
    ) -> int:
        """Delete every experiment owned by `user_id`. Returns rowcount.

        B8: triggered by Celery task `cleanup_orphaned_experiments` after a
        user is removed from users_db. `experiment_images` cascade-delete
        via ORM `cascade="all, delete-orphan"`.
        """
        stmt = delete(Experiment).where(Experiment.user_id == user_id)
        result = await session.execute(stmt)
        await self.invalidate_cache()
        return int(getattr(result, "rowcount", 0) or 0)


# Hint for the unused `CursorResult` import (kept for future typing of rowcount).
_ = CursorResult
