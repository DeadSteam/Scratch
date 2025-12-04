from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from .base import SchemaBase
from .film import FilmRead
from .equipment_config import EquipmentConfigRead
# Note: UserRead not imported - users are in a separate database


class ScratchResult(SchemaBase):
    """Single scratch analysis result."""
    image_id: UUID = Field(..., description="Image UUID")
    scratch_index: float = Field(..., ge=0, le=1, description="Calculated scratch index (0-1)")


class ExperimentBase(SchemaBase):
    film_id: UUID = Field(..., description="ID of the film used in experiment")
    config_id: UUID = Field(..., description="ID of the equipment configuration")
    user_id: UUID = Field(..., description="ID of the user conducting the experiment")
    name: Optional[str] = Field(None, max_length=200, description="Experiment name")
    date: Optional[datetime] = Field(None, description="Experiment date and time")
    rect_coords: Optional[list[float]] = Field(None, description="Rectangle coordinates for analysis [x, y, width, height]")
    weight: Optional[float] = Field(None, gt=0, description="Sample weight in grams")
    has_fabric: Optional[bool] = Field(False, description="Whether fabric substrate was used")
    scratch_results: Optional[list[Dict[str, Any]]] = Field(None, description="Array of scratch analysis results for each image")


class ExperimentCreate(ExperimentBase):
    @field_validator('rect_coords')
    @classmethod
    def validate_rect_coords(cls, v: Optional[list[float]]) -> Optional[list[float]]:
        """Validate rectangle coordinates have correct format."""
        if v is not None:
            if len(v) != 4:
                raise ValueError('Rectangle coordinates must contain exactly 4 values: [x, y, width, height]')
            if any(coord < 0 for coord in v):
                raise ValueError('Rectangle coordinates must be non-negative')
        return v


class ExperimentUpdate(SchemaBase):
    film_id: Optional[UUID] = None
    config_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    name: Optional[str] = Field(None, max_length=200)
    date: Optional[datetime] = None
    rect_coords: Optional[list[float]] = None
    weight: Optional[float] = None
    has_fabric: Optional[bool] = None
    scratch_results: Optional[list[Dict[str, Any]]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty string to None."""
        if v == '':
            return None
        return v

    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        """Validate weight is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Weight must be greater than 0')
        return v


class ExperimentRead(ExperimentBase):
    id: UUID
    film: Optional[FilmRead] = None
    config: Optional[EquipmentConfigRead] = None
    # Note: No user relationship - users are in a separate database (users_db)



