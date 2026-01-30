"""Knowledge base models: Situation, Cause, Advice."""

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class Situation(Base):
    """Ситуации (родительская таблица для cause)."""

    __tablename__ = "situation"

    situation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    controlled_param: Mapped[str | None] = mapped_column(String(100), nullable=True)
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(String(100), nullable=True)

    causes: Mapped[list["Cause"]] = relationship(
        back_populates="situation",
        cascade="all, delete-orphan",
    )


class Cause(Base):
    """Причины (родитель для advice, дочерняя для situation)."""

    __tablename__ = "cause"

    cause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    situation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("situation.situation_id", ondelete="CASCADE"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(String(100), nullable=True)

    situation: Mapped[Optional["Situation"]] = relationship(back_populates="causes")
    advices: Mapped[list["Advice"]] = relationship(
        back_populates="cause",
        cascade="all, delete-orphan",
    )


class Advice(Base):
    """Рекомендации (дочерняя таблица для cause)."""

    __tablename__ = "advice"

    advice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cause_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cause.cause_id", ondelete="CASCADE"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(String(50), nullable=True)

    cause: Mapped[Optional["Cause"]] = relationship(back_populates="advices")
