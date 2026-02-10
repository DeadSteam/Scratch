"""Knowledge base models: Situation, Cause, Advice.

All tables now use a standard ``id`` UUID primary key inherited from
``UUIDBase``, matching the convention used by every other table in the
project.
"""

import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import UUIDBase


class Situation(UUIDBase):
    """Ситуации (родительская таблица для cause)."""

    __tablename__ = "situation"

    controlled_param: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    causes: Mapped[list["Cause"]] = relationship(
        back_populates="situation",
        cascade="all, delete-orphan",
    )


class Cause(UUIDBase):
    """Причины (родитель для advice, дочерняя для situation)."""

    __tablename__ = "cause"

    situation_id: Mapped["uuid.UUID | None"] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("situation.id", ondelete="CASCADE"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    situation: Mapped["Situation | None"] = relationship(
        back_populates="causes"
    )
    advices: Mapped[list["Advice"]] = relationship(
        back_populates="cause",
        cascade="all, delete-orphan",
    )


class Advice(UUIDBase):
    """Рекомендации (дочерняя таблица для cause)."""

    __tablename__ = "advice"

    cause_id: Mapped["uuid.UUID | None"] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cause.id", ondelete="CASCADE"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    cause: Mapped["Cause | None"] = relationship(back_populates="advices")
