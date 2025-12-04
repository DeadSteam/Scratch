from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import UUIDBase


class EquipmentConfig(UUIDBase):
    __tablename__ = "equipment_configs"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    head_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # связь с экспериментами
    experiments: Mapped[List["Experiment"]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )
