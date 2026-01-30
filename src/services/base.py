"""Base service class with common patterns."""

from typing import Any, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.base import BaseRepositoryImpl
from ..schemas.base import SchemaBase
from .exceptions import NotFoundError

T = TypeVar("T")  # ORM Model type
CreateSchema = TypeVar("CreateSchema", bound=SchemaBase)
UpdateSchema = TypeVar("UpdateSchema", bound=SchemaBase)
ReadSchema = TypeVar("ReadSchema", bound=SchemaBase)


class BaseService[T, CreateSchema, UpdateSchema, ReadSchema]:
    """Base service with common CRUD operations."""

    def __init__(
        self,
        repository: BaseRepositoryImpl[T],
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
        """Get entity by ID."""
        entity = await self.repository.get_by_id(entity_id, session)
        if not entity:
            raise NotFoundError(self.entity_name, entity_id)
        return cast(ReadSchema, self.read_schema.model_validate(entity))

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ReadSchema]:
        """Get all entities with pagination."""
        entities = await self.repository.get_all(session, skip, limit)
        return [self.read_schema.model_validate(e) for e in entities]

    async def create(self, data: CreateSchema, session: AsyncSession) -> ReadSchema:
        """Create new entity."""
        # Convert Pydantic model to dict (SchemaBase extends BaseModel)
        entity_data = cast(BaseModel, data).model_dump(exclude_unset=True)

        # Check for uniqueness if needed (override in subclass)
        await self._check_unique_constraints(entity_data, session)

        # Create entity
        entity = await self.repository.create(entity_data, session)
        return cast(ReadSchema, self.read_schema.model_validate(entity))

    async def update(
        self, entity_id: UUID, data: UpdateSchema, session: AsyncSession
    ) -> ReadSchema:
        """Update entity by ID."""
        # Check if entity exists
        if not await self.repository.exists(entity_id, session):
            raise NotFoundError(self.entity_name, entity_id)

        # Convert Pydantic model to dict (SchemaBase extends BaseModel)
        entity_data = cast(BaseModel, data).model_dump(exclude_unset=True)

        if not entity_data:
            # No fields to update, just return current entity
            return await self.get_by_id(entity_id, session)

        # Check for uniqueness if needed
        await self._check_unique_constraints(entity_data, session, entity_id)

        # Update entity
        entity = await self.repository.update(entity_id, entity_data, session)
        return cast(ReadSchema, self.read_schema.model_validate(entity))

    async def delete(self, entity_id: UUID, session: AsyncSession) -> bool:
        """Delete entity by ID."""
        # Check if entity exists
        if not await self.repository.exists(entity_id, session):
            raise NotFoundError(self.entity_name, entity_id)

        return cast(bool, await self.repository.delete(entity_id, session))

    async def _check_unique_constraints(
        self,
        data: dict[str, Any],
        session: AsyncSession,
        exclude_id: UUID | None = None,
    ) -> None:
        """
        Check unique constraints before create/update.
        Override in subclass to implement specific checks.
        """
        pass
