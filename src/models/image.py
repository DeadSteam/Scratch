from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    LargeBinary,
    String,
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
    # B11: original MIME captured at upload time. NULL for legacy rows; the
    # download endpoint falls back to magic-byte sniffing in that case.
    mime_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    passes: Mapped[int] = mapped_column(Integer, default=1)

    experiment: Mapped[Experiment] = relationship(back_populates="images")
