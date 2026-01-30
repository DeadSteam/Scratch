from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    LargeBinary,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import UUIDBase

if TYPE_CHECKING:
    from .experiment import Experiment


class ExperimentImage(UUIDBase):
    __tablename__ = "experiment_images"

    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
    )

    image_data: Mapped[bytes] = mapped_column(
        # LargeBinary = BYTEA в PostgreSQL
        type_=LargeBinary,
        nullable=False,
    )
    passes: Mapped[int] = mapped_column(Integer, default=1)

    experiment: Mapped[Experiment] = relationship(back_populates="images")
