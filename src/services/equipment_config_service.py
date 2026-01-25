"""Equipment configuration service."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.equipment_config import EquipmentConfig
from ..repositories.equipment_config_repository import EquipmentConfigRepository
from ..schemas.equipment_config import (
    EquipmentConfigCreate,
    EquipmentConfigRead,
    EquipmentConfigUpdate,
)
from .base import BaseService
from .exceptions import AlreadyExistsError


class EquipmentConfigService(
    BaseService[EquipmentConfig, EquipmentConfigCreate, EquipmentConfigUpdate, EquipmentConfigRead]
):
    """Equipment configuration service."""

    def __init__(self, repository: EquipmentConfigRepository):
        super().__init__(
            repository=repository,
            entity_name="EquipmentConfig",
            create_schema=EquipmentConfigCreate,
            update_schema=EquipmentConfigUpdate,
            read_schema=EquipmentConfigRead,
        )
        self.config_repo = repository

    async def _check_unique_constraints(
        self, data: dict[str, Any], session: AsyncSession, exclude_id: UUID | None = None
    ) -> None:
        """Check config name uniqueness."""
        if "name" in data:
            existing = await self.config_repo.get_by_name(data["name"], session)
            if existing and (not exclude_id or existing.id != exclude_id):
                raise AlreadyExistsError("EquipmentConfig", "name", data["name"])

    async def search_by_name(
        self, name_pattern: str, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[EquipmentConfigRead]:
        """Search equipment configs by name pattern."""
        configs = await self.config_repo.search_by_name(name_pattern, session, skip, limit)
        return [self.read_schema.model_validate(c) for c in configs]

    async def get_by_head_type(
        self, head_type: str, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[EquipmentConfigRead]:
        """Get configs by head type."""
        configs = await self.config_repo.get_by_head_type(head_type, session, skip, limit)
        return [self.read_schema.model_validate(c) for c in configs]
