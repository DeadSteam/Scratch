from __future__ import annotations

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from .experiment import Experiment


class EquipmentConfig(UUIDBase):
    __tablename__ = "equipment_configs"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    head_type: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)

    # связь с экспериментами
    experiments: Mapped[list[Experiment]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )
