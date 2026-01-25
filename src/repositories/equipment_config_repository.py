from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.equipment_config import EquipmentConfig
from .base import CachedRepositoryImpl


class EquipmentConfigRepository(CachedRepositoryImpl[EquipmentConfig]):
    """Equipment configuration repository implementation."""

    def __init__(self) -> None:
        super().__init__(EquipmentConfig)

    async def get_by_name(self, name: str, session: AsyncSession) -> EquipmentConfig | None:
        """Get equipment config by name."""
        result = await session.execute(select(EquipmentConfig).where(EquipmentConfig.name == name))
        return result.scalar_one_or_none()

    async def search_by_name(
        self, name_pattern: str, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[EquipmentConfig]:
        """Search equipment configs by name pattern."""
        result = await session.execute(
            select(EquipmentConfig)
            .where(EquipmentConfig.name.ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_head_type(
        self, head_type: str, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[EquipmentConfig]:
        """Get equipment configs by head type."""
        result = await session.execute(
            select(EquipmentConfig)
            .where(EquipmentConfig.head_type == head_type)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
