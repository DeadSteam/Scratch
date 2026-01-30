"""API error handlers."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from ..services.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ServiceException,
    ValidationError,
)
from .responses import ErrorDetail, ErrorResponse


async def service_exception_handler(
    request: Request, exc: ServiceException
) -> JSONResponse:
    """Handle service layer exceptions."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, AlreadyExistsError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, ConflictError):
        status_code = status.HTTP_409_CONFLICT

    error_response = ErrorResponse(
        success=False, message=exc.message, detail=exc.details, errors=None
    )

    return JSONResponse(status_code=status_code, content=error_response.model_dump())


async def validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = [
        ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            type=error["type"],
        )
        for error in exc.errors()
    ]

    error_response = ErrorResponse(
        success=False, message="Validation error", errors=errors, detail=None
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )
