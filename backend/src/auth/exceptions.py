from __future__ import annotations

from core.exceptions import MoggedError


class InvalidCredentialsError(MoggedError):
    """Raised when login credentials are wrong."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InvalidTokenError(MoggedError):
    """Raised when a JWT is missing, expired, or malformed."""

    def __init__(self) -> None:
        super().__init__("Invalid or expired token")
