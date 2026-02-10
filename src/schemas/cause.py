"""Cause schemas."""

from uuid import UUID

from pydantic import Field

from .base import SchemaBase


class CauseBase(SchemaBase):
    situation_id: UUID | None = Field(None, description="Ссылка на ситуацию")
    description: str | None = Field(
        None, max_length=100, description="Описание причины"
    )


class CauseCreate(CauseBase):
    pass


class CauseUpdate(SchemaBase):
    situation_id: UUID | None = None
    description: str | None = Field(None, max_length=100)


class CauseRead(CauseBase):
    id: UUID
