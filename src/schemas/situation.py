"""Situation schemas."""

from uuid import UUID

from pydantic import Field

from .base import SchemaBase


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


class SituationCreate(SituationBase):
    pass


class SituationUpdate(SchemaBase):
    controlled_param: str | None = Field(None, max_length=100)
    min_value: float | None = None
    max_value: float | None = None
    label: str | None = Field(None, max_length=50)
    severity: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=255)


class SituationRead(SituationBase):
    id: UUID
