from __future__ import annotations

from core.exceptions import MoggedError


class NotOrgMemberError(MoggedError):
    """Raised when a user is not a member of the organization."""

    def __init__(self) -> None:
        super().__init__("You are not a member of this organization")


class InsufficientOrgRoleError(MoggedError):
    """Raised when a member lacks the required role for an action."""

    def __init__(self, required: str = "admin") -> None:
        super().__init__(f"This action requires {required} role or higher")
