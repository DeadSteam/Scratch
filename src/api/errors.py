"""API error handlers."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from ..services.exceptions import ServiceError
from .responses import ErrorDetail, ErrorResponse


async def service_exception_handler(
    request: Request, exc: ServiceError
) -> JSONResponse:
    """Handle service layer exceptions using status_code from exception class."""
    error_response = ErrorResponse(
        success=False, message=exc.message, detail=exc.details, errors=None
    )

    response = JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )

    # Attach headers (e.g. WWW-Authenticate for 401)
    for key, value in exc.headers.items():
        response.headers[key] = value

    return response


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
