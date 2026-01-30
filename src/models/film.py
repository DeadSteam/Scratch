from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Float,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import UUIDBase

if TYPE_CHECKING:
    from .experiment import Experiment


class Film(UUIDBase):
    __tablename__ = "films"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    coating_name: Mapped[str | None] = mapped_column(String(100))
    coating_thickness: Mapped[float | None] = mapped_column(Float)

    # relation to experiments
    experiments: Mapped[list[Experiment]] = relationship(
        back_populates="film", cascade="all, delete-orphan"
    )
