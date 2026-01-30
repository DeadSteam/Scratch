"""Base repository for knowledge base entities (UUID PK)."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class KnowledgeRepositoryBase(Generic[T]):
    """Base repository for Situation, Cause, Advice (UUID PK, no Redis)."""

    def __init__(self, model: type[T], pk_name: str):
        self.model = model
        self.pk_name = pk_name

    @property
    def pk_column(self) -> Any:
        return getattr(self.model, self.pk_name)

    async def get_by_id(self, id: UUID, session: AsyncSession) -> T | None:
        result = await session.execute(select(self.model).where(self.pk_column == id))
        return result.scalar_one_or_none()

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        result = await session.execute(
            select(self.model).order_by(self.pk_column).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any], session: AsyncSession) -> T:
        stmt = insert(self.model).values(**data).returning(*self.model.__table__.c)
        result = await session.execute(stmt)
        await session.commit()
        row = result.one()
        return self.model(**row._mapping)

    async def update(
        self, id: UUID, data: dict[str, Any], session: AsyncSession
    ) -> T | None:
        stmt = (
            update(self.model)
            .where(self.pk_column == id)
            .values(**data)
            .returning(*self.model.__table__.c)
        )
        result = await session.execute(stmt)
        await session.commit()
        row = result.one_or_none()
        return self.model(**row._mapping) if row is not None else None

    async def delete(self, id: UUID, session: AsyncSession) -> bool:
        stmt = delete(self.model).where(self.pk_column == id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

    async def exists(self, id: UUID, session: AsyncSession) -> bool:
        result = await session.execute(
            select(self.pk_column).where(self.pk_column == id)
        )
        return result.scalar_one_or_none() is not None
