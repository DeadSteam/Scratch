from typing import List, Optional
from sqlalchemy import (
    String,
    Float,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from .base import UUIDBase


class Film(UUIDBase):
    __tablename__ = "films"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    coating_name: Mapped[Optional[str]] = mapped_column(String(100))
    coating_thickness: Mapped[Optional[float]] = mapped_column(Float)

    # связь с экспериментами
    experiments: Mapped[List["Experiment"]] = relationship(
        back_populates="film", cascade="all, delete-orphan"
    )
