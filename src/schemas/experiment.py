from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from .advice import AdviceRead
from .base import SchemaBase
from .cause import CauseRead
from .equipment_config import EquipmentConfigRead
from .film import FilmRead
from .situation import SituationRead

# Note: UserRead not imported - users are in a separate database


class ScratchResult(SchemaBase):
    """Single scratch analysis result."""

    image_id: UUID = Field(..., description="Image UUID")
    passes: int | None = Field(None, ge=0, description="Number of passes for the image")
    scratch_index: float = Field(
        ..., ge=0, le=1, description="Calculated scratch index (0-1)"
    )
    total_pixels: int | None = Field(
        None,
        ge=0,
        description="Pixel count used in analysis",
    )


class KnowledgeCauseRead(CauseRead):
    advices: list[AdviceRead] = Field(default_factory=list, description="Cause advices")


class KnowledgeSummary(SchemaBase):
    controlled_param: str | None = Field(
        None, description="Controlled parameter used to resolve knowledge situation"
    )
    delta: float | None = Field(
        None, description="Difference between latest image and reference image"
    )
    reference_result: ScratchResult | None = Field(
        None, description="Reference image analysis result"
    )
    latest_result: ScratchResult | None = Field(
        None, description="Latest image analysis result"
    )
    situation: SituationRead | None = Field(
        None, description="Matched knowledge base situation"
    )
    causes: list[KnowledgeCauseRead] = Field(
        default_factory=list, description="Possible causes with advices"
    )


def _validate_rect_coords(v: list[float] | None) -> list[float] | None:
    if v is None:
        return v
    if len(v) != 4:
        raise ValueError("Rectangle must have 4 values: [x, y, width, height]")
    if any(coord < 0 for coord in v):
        raise ValueError("Rectangle coordinates must be non-negative")
    return v


class _ExperimentEditable(SchemaBase):
    """Fields a user is allowed to set/edit. Excludes user_id and scratch_results."""

    film_id: UUID = Field(..., description="ID of the film used in experiment")
    config_id: UUID = Field(..., description="ID of the equipment configuration")
    name: str | None = Field(None, max_length=200, description="Experiment name")
    date: datetime | None = Field(None, description="Experiment date and time")
    rect_coords: list[float] | None = Field(
        None, description="Rectangle coordinates for analysis [x, y, width, height]"
    )
    weight: float | None = Field(None, gt=0, description="Sample weight in grams")
    has_fabric: bool | None = Field(
        False, description="Whether fabric substrate was used"
    )


class ExperimentCreate(_ExperimentEditable):
    """Create payload. `user_id` is injected from the authenticated current_user."""

    @field_validator("rect_coords")
    @classmethod
    def _check_rect(cls, v: list[float] | None) -> list[float] | None:
        return _validate_rect_coords(v)


class ExperimentUpdate(SchemaBase):
    """PATCH payload.

    SECURITY: must NOT include `user_id` (impersonation) or
    `scratch_results` (analysis fabrication). Both are set server-side.
    """

    film_id: UUID | None = None
    config_id: UUID | None = None
    name: str | None = Field(None, max_length=200)
    date: datetime | None = None
    rect_coords: list[float] | None = None
    weight: float | None = Field(None, gt=0)
    has_fabric: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Convert empty string to None."""
        if v == "":
            return None
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Weight must be greater than 0")
        return v

    @field_validator("rect_coords")
    @classmethod
    def _check_rect(cls, v: list[float] | None) -> list[float] | None:
        return _validate_rect_coords(v)


class ExperimentRead(_ExperimentEditable):
    """Server-rendered view; includes server-set fields."""

    id: UUID
    user_id: UUID
    scratch_results: list[dict[str, Any]] | None = None
    film: FilmRead | None = None
    config: EquipmentConfigRead | None = None
    knowledge_summary: KnowledgeSummary | None = None
