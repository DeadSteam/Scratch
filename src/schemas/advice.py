"""Advice schemas."""

from uuid import UUID

from pydantic import Field

from .base import SchemaBase


class AdviceBase(SchemaBase):
    cause_id: UUID | None = Field(None, description="Ссылка на причину")
    description: str | None = Field(None, max_length=50, description="Текст рекомендации")


class AdviceCreate(AdviceBase):
    pass


class AdviceUpdate(SchemaBase):
    cause_id: UUID | None = None
    description: str | None = Field(None, max_length=50)


class AdviceRead(AdviceBase):
    advice_id: UUID
