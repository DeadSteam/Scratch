"""Common API response models."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """Generic API response."""

    success: bool = Field(True, description="Operation success status")
    message: str | None = Field(None, description="Response message")
    data: T | None = Field(None, description="Response data")


class ErrorDetail(BaseModel):
    """Error detail model."""

    field: str | None = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: str | None = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(False, description="Operation success status")
    message: str = Field(..., description="Error message")
    errors: list[ErrorDetail] | None = Field(None, description="Detailed errors")
    detail: dict[str, Any] | None = Field(None, description="Additional error details")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    success: bool = Field(True, description="Operation success status")
    data: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of skipped items")
    limit: int = Field(..., description="Page size limit")
    has_more: bool = Field(..., description="Whether there are more items")
