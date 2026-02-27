from __future__ import annotations


class MoggedError(Exception):
    """Base exception for all mogged.tv domain errors."""

    def __init__(self, message: str = "An error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(MoggedError):
    """Raised when a requested resource does not exist."""

    def __init__(self, entity: str, **filters: object) -> None:
        self.entity = entity
        self.filters = filters
        super().__init__(f"{entity} not found")


class AlreadyExistsError(MoggedError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(self, entity: str, field: str, value: object) -> None:
        self.entity = entity
        self.field = field
        self.value = value
        super().__init__(f"{entity} already exists")


class PermissionDeniedError(MoggedError):
    """Raised when a user lacks permission for an action."""


class ValidationError(MoggedError):
    """Raised when domain validation fails."""
