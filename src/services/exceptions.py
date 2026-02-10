"""Service layer exceptions."""

from typing import Any
from uuid import UUID


class ServiceError(Exception):
    """Base exception for service layer."""

    status_code: int = 500

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.message = message
        self.details = details or {}
        self.headers = headers or {}
        super().__init__(self.message)


class NotFoundError(ServiceError):
    """Entity not found exception."""

    status_code = 404

    def __init__(self, entity_name: str, entity_id: UUID | str):
        message = f"{entity_name} with id {entity_id} not found"
        super().__init__(message, {"entity": entity_name, "id": str(entity_id)})


class AlreadyExistsError(ServiceError):
    """Entity already exists exception."""

    status_code = 409

    def __init__(self, entity_name: str, field: str, value: Any):
        message = f"{entity_name} with {field}='{value}' already exists"
        super().__init__(
            message, {"entity": entity_name, "field": field, "value": value}
        )


class AuthenticationError(ServiceError):
    """Authentication failed exception."""

    status_code = 401

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, headers={"WWW-Authenticate": "Bearer"})


class AuthorizationError(ServiceError):
    """Authorization failed exception."""

    status_code = 403

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


class ValidationError(ServiceError):
    """Business logic validation error."""

    status_code = 400

    def __init__(self, message: str, field: str | None = None):
        details = {"field": field} if field else {}
        super().__init__(message, details)


class ConflictError(ServiceError):
    """Conflict in business logic."""

    status_code = 409

    def __init__(self, message: str):
        super().__init__(message)
