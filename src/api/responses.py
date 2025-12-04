"""Common API response models."""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """Generic API response."""
    success: bool = Field(True, description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")


class ErrorDetail(BaseModel):
    """Error detail model."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Operation success status")
    message: str = Field(..., description="Error message")
    errors: Optional[list[ErrorDetail]] = Field(None, description="Detailed errors")
    detail: Optional[dict[str, Any]] = Field(None, description="Additional error details")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    success: bool = Field(True, description="Operation success status")
    data: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of skipped items")
    limit: int = Field(..., description="Page size limit")
    has_more: bool = Field(..., description="Whether there are more items")




















