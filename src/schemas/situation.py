"""Situation schemas."""

from uuid import UUID

from pydantic import Field, field_validator

from .base import SchemaBase


def _round_bound(v: float | None) -> float | None:
    """Limit a knowledge-rule range bound to 3 decimals.

    Situation bounds are compared against the scratch delta, which is itself
    rounded to 3 decimals; keeping the rules at the same precision avoids
    off-by-a-rounding mismatches at range edges.
    """
    return round(v, 3) if v is not None else None


class SituationBase(SchemaBase):
    controlled_param: str | None = Field(
        None, max_length=100, description="Контролируемый параметр"
    )
    min_value: float | None = Field(None, description="Минимальное значение диапазона")
    max_value: float | None = Field(None, description="Максимальное значение диапазона")
    label: str | None = Field(None, max_length=50, description="Оценка для UI")
    severity: str | None = Field(
        None,
        max_length=20,
        description="Уровень серьезности для UI: success/warning/error/muted",
    )
    description: str | None = Field(None, max_length=255, description="Описание")

    @field_validator("min_value", "max_value")
    @classmethod
    def _round_bounds(cls, v: float | None) -> float | None:
        return _round_bound(v)


class SituationCreate(SituationBase):
    pass


class SituationUpdate(SchemaBase):
    controlled_param: str | None = Field(None, max_length=100)
    min_value: float | None = None
    max_value: float | None = None
    label: str | None = Field(None, max_length=50)
    severity: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=255)

    @field_validator("min_value", "max_value")
    @classmethod
    def _round_bounds(cls, v: float | None) -> float | None:
        return _round_bound(v)


class SituationRead(SituationBase):
    id: UUID
