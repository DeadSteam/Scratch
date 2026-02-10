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
    description: str | None = Field(None, max_length=100, description="Описание")


class SituationCreate(SituationBase):
    pass


class SituationUpdate(SchemaBase):
    controlled_param: str | None = Field(None, max_length=100)
    min_value: float | None = None
    max_value: float | None = None
    description: str | None = Field(None, max_length=100)


class SituationRead(SituationBase):
    id: UUID
