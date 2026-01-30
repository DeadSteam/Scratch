"""Service layer exceptions."""

from typing import Any
from uuid import UUID


class ServiceException(Exception):
    """Base exception for service layer."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ServiceException):
    """Entity not found exception."""

    def __init__(self, entity_name: str, entity_id: UUID):
        message = f"{entity_name} with id {entity_id} not found"
        super().__init__(message, {"entity": entity_name, "id": str(entity_id)})


class AlreadyExistsError(ServiceException):
    """Entity already exists exception."""

    def __init__(self, entity_name: str, field: str, value: Any):
        message = f"{entity_name} with {field}='{value}' already exists"
        super().__init__(
            message, {"entity": entity_name, "field": field, "value": value}
        )


class AuthenticationError(ServiceException):
    """Authentication failed exception."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class AuthorizationError(ServiceException):
    """Authorization failed exception."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


class ValidationError(ServiceException):
    """Business logic validation error."""

    def __init__(self, message: str, field: str | None = None):
        details = {"field": field} if field else {}
        super().__init__(message, details)


class ConflictError(ServiceException):
    """Conflict in business logic."""

    def __init__(self, message: str):
        super().__init__(message)
