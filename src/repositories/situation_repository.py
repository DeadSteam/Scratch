"""Situation repository."""

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.knowledge import Situation
from .base import CachedRepositoryImpl


class SituationRepository(CachedRepositoryImpl[Situation]):
    def __init__(self) -> None:
        super().__init__(Situation)

    async def find_by_controlled_value(
        self,
        controlled_param: str,
        value: float,
        session: AsyncSession,
    ) -> Situation | None:
        stmt: Select[tuple[Situation]] = (
            select(Situation)
            .where(Situation.controlled_param == controlled_param)
            .where(or_(Situation.min_value.is_(None), Situation.min_value <= value))
            .where(or_(Situation.max_value.is_(None), Situation.max_value >= value))
            .order_by(
                Situation.min_value.desc().nullslast(),
                Situation.max_value.asc().nullsfirst(),
                Situation.id.asc(),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_by_value_in_ranges(
        self,
        value: float,
        session: AsyncSession,
    ) -> Situation | None:
        """Pick a situation by min/max only (delta scratch-index use case).

        ``controlled_param`` is ignored. Rows with both bounds unset are excluded.
        """
        stmt: Select[tuple[Situation]] = (
            select(Situation)
            .where(
                or_(Situation.min_value.isnot(None), Situation.max_value.isnot(None))
            )
            .where(or_(Situation.min_value.is_(None), Situation.min_value <= value))
            .where(or_(Situation.max_value.is_(None), Situation.max_value >= value))
            .order_by(
                Situation.min_value.desc().nullslast(),
                Situation.max_value.asc().nullsfirst(),
                Situation.id.asc(),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().first()
