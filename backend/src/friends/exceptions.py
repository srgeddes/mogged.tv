from __future__ import annotations

from core.exceptions import MoggedError


class AlreadyFriendsError(MoggedError):
    """Raised when users are already friends."""

    def __init__(self) -> None:
        super().__init__("You're already friends with this user")


class FriendRequestExistsError(MoggedError):
    """Raised when a pending friend request already exists."""

    def __init__(self) -> None:
        super().__init__("A friend request already exists between you and this user")


class CannotFriendSelfError(MoggedError):
    """Raised when a user tries to friend themselves."""

    def __init__(self) -> None:
        super().__init__("You can't send a friend request to yourself")
