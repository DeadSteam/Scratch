from typing import Optional
from uuid import UUID

from pydantic import Field, field_validator

from .base import SchemaBase


class ExperimentImageBase(SchemaBase):
    experiment_id: UUID = Field(..., description="ID of the related experiment")
    image_data: bytes = Field(..., description="Binary image data")
    passes: int = Field(0, ge=0, le=1000, description="Number of passes (0 for reference image)")


class ExperimentImageCreate(ExperimentImageBase):
    @field_validator('image_data')
    @classmethod
    def validate_image_size(cls, v: bytes) -> bytes:
        """Validate image data size."""
        max_size = 10 * 1024 * 1024  # 10MB
        if len(v) > max_size:
            raise ValueError(f'Image size must not exceed {max_size} bytes (10MB)')
        if len(v) == 0:
            raise ValueError('Image data cannot be empty')
        return v


class ExperimentImageUpdate(SchemaBase):
    experiment_id: Optional[UUID] = None
    image_data: Optional[bytes] = None
    passes: Optional[int] = Field(None, ge=0, le=1000)
    
    @field_validator('image_data')
    @classmethod
    def validate_image_size(cls, v: Optional[bytes]) -> Optional[bytes]:
        """Validate image data size if provided."""
        if v is not None:
            max_size = 10 * 1024 * 1024  # 10MB
            if len(v) > max_size:
                raise ValueError(f'Image size must not exceed {max_size} bytes (10MB)')
            if len(v) == 0:
                raise ValueError('Image data cannot be empty')
        return v


class ExperimentImageRead(SchemaBase):
    id: UUID
    experiment_id: UUID
    passes: int



