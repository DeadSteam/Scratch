from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP, UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import UUIDBase

if TYPE_CHECKING:
    from .equipment_config import EquipmentConfig
    from .film import Film
    from .image import ExperimentImage


class Experiment(UUIDBase):
    __tablename__ = "experiments"

    film_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("films.id", ondelete="CASCADE"), nullable=False
    )
    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("equipment_configs.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Note: user_id references users in a separate database (users_db)
    # No ForeignKey constraint as users are in a different database
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    rect_coords: Mapped[list[float] | None] = mapped_column(ARRAY(Float))
    weight: Mapped[float | None] = mapped_column(Float)
    has_fabric: Mapped[bool] = mapped_column(Boolean, default=False)

    # Scratch analysis results: list of scratch_index per image.
    # Structure: [{"image_id": "uuid", "scratch_index": 0.0342}, ...]
    scratch_results: Mapped[list[dict[str, object]] | None] = mapped_column(
        JSON, nullable=True
    )

    # связи
    film: Mapped[Film] = relationship(back_populates="experiments")
    config: Mapped[EquipmentConfig] = relationship(back_populates="experiments")
    # Note: No user relationship as users are in a separate database (users_db)
    images: Mapped[list[ExperimentImage]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )
