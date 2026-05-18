from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.equipment_config import EquipmentConfig
from .base import CachedRepositoryImpl
from .named_entity import NamedEntityRepositoryMixin


class EquipmentConfigRepository(
    NamedEntityRepositoryMixin, CachedRepositoryImpl[EquipmentConfig]
):
    """Equipment configuration repository implementation."""

    def __init__(self) -> None:
        super().__init__(EquipmentConfig)

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
