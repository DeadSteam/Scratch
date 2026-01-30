"""Base service for knowledge base entities (UUID)."""

from typing import Any, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.knowledge_repository_base import KnowledgeRepositoryBase
from ..schemas.base import SchemaBase
from .exceptions import NotFoundError

T = TypeVar("T")
CreateSchema = TypeVar("CreateSchema", bound=SchemaBase)
UpdateSchema = TypeVar("UpdateSchema", bound=SchemaBase)
ReadSchema = TypeVar("ReadSchema", bound=SchemaBase)


class KnowledgeServiceBase[T, CreateSchema, UpdateSchema, ReadSchema]:
    """Base service for Situation, Cause, Advice (UUID PK)."""

    def __init__(
        self,
        repository: KnowledgeRepositoryBase,
        entity_name: str,
        create_schema: type[CreateSchema],
        update_schema: type[UpdateSchema],
        read_schema: type[ReadSchema],
    ):
        self.repository = repository
        self.entity_name = entity_name
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema

    async def get_by_id(self, entity_id: UUID, session: AsyncSession) -> ReadSchema:
        entity = await self.repository.get_by_id(entity_id, session)
        if not entity:
            raise NotFoundError(self.entity_name, entity_id)
        return cast(ReadSchema, self.read_schema.model_validate(entity))

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ReadSchema]:
        entities = await self.repository.get_all(session, skip, limit)
        return [self.read_schema.model_validate(e) for e in entities]

    async def create(self, data: CreateSchema, session: AsyncSession) -> ReadSchema:
        entity_data = cast(BaseModel, data).model_dump(exclude_unset=True)
        await self._check_constraints(entity_data, session)
        entity = await self.repository.create(entity_data, session)
        return cast(ReadSchema, self.read_schema.model_validate(entity))

    async def update(
        self, entity_id: UUID, data: UpdateSchema, session: AsyncSession
    ) -> ReadSchema:
        if not await self.repository.exists(entity_id, session):
            raise NotFoundError(self.entity_name, entity_id)
        entity_data = cast(BaseModel, data).model_dump(exclude_unset=True)
        if not entity_data:
            return await self.get_by_id(entity_id, session)
        await self._check_constraints(entity_data, session, entity_id)
        entity = await self.repository.update(entity_id, entity_data, session)
        return cast(ReadSchema, self.read_schema.model_validate(entity))

    async def delete(self, entity_id: UUID, session: AsyncSession) -> bool:
        if not await self.repository.exists(entity_id, session):
            raise NotFoundError(self.entity_name, entity_id)
        return cast(bool, await self.repository.delete(entity_id, session))

    async def _check_constraints(
        self,
        data: dict[str, Any],
        session: AsyncSession,
        exclude_id: UUID | None = None,
    ) -> None:
        """Override in subclass for FK checks etc."""
        pass
