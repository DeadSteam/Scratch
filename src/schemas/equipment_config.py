from uuid import UUID

from pydantic import Field

from .base import SchemaBase


class EquipmentConfigBase(SchemaBase):
    name: str = Field(..., min_length=1, max_length=100, description="Equipment configuration name")
    head_type: str | None = Field(None, max_length=100, description="Type of equipment head")
    description: str | None = Field(None, description="Detailed description of the configuration")


class EquipmentConfigCreate(EquipmentConfigBase):
    pass


class EquipmentConfigUpdate(SchemaBase):
    name: str | None = Field(None, min_length=1, max_length=100)
    head_type: str | None = Field(None, max_length=100)
    description: str | None = None


class EquipmentConfigRead(EquipmentConfigBase):
    id: UUID
