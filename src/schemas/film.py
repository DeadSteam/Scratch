from uuid import UUID

from pydantic import Field, ValidationInfo, field_validator

from .base import SchemaBase


class FilmBase(SchemaBase):
    name: str = Field(..., min_length=1, max_length=100, description="Film name")
    coating_name: str | None = Field(
        None, max_length=100, description="Coating material name"
    )
    coating_thickness: float | None = Field(
        None, gt=0, description="Coating thickness in micrometers"
    )


class FilmCreate(FilmBase):
    @field_validator("coating_thickness")
    @classmethod
    def validate_thickness_with_coating(
        cls, v: float | None, info: ValidationInfo
    ) -> float | None:
        """Ensure coating_thickness is provided if coating_name is set."""
        if "coating_name" in info.data and info.data["coating_name"] and v is None:
            raise ValueError(
                "coating_thickness must be provided when coating_name is set"
            )
        return v


class FilmUpdate(SchemaBase):
    name: str | None = Field(None, min_length=1, max_length=100)
    coating_name: str | None = Field(None, max_length=100)
    coating_thickness: float | None = Field(None, gt=0)


class FilmRead(FilmBase):
    id: UUID
