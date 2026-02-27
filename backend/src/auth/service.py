from __future__ import annotations

from uuid import UUID

from core.exceptions import AlreadyExistsError, ValidationError
from core.security import create_access_token, hash_password, verify_password
from users.models import User
from users.repository import UserRepository

from .exceptions import InvalidCredentialsError, InvalidTokenError

RESERVED_USERNAMES = frozenset(
    {
        "login",
        "signup",
        "home",
        "stream",
        "health",
        "api",
        "admin",
        "settings",
        "profile",
        "aura",
        "trivia",
    }
)

_DUMMY_HASH = hash_password("timing-attack-dummy")


async def signup(
    repo: UserRepository,
    username: str,
    email: str,
    password: str,
    display_name: str | None = None,
) -> tuple[str, User]:
    if username.lower() in RESERVED_USERNAMES:
        raise ValidationError("This username is reserved")

    username_taken = await repo.username_exists(username)
    email_taken = await repo.email_exists(email)
    if username_taken or email_taken:
        raise AlreadyExistsError("User", "credentials", "")

    user = await repo.create(
        username=username,
        email=email,
        password_hash=hash_password(password),
        display_name=display_name or username,
    )
    token = create_access_token(user.id, user.username)
    return token, user


async def login(repo: UserRepository, email: str, password: str) -> tuple[str, User]:
    user = await repo.get_or_none(email=email)
    pw_hash = user.password_hash if user is not None else _DUMMY_HASH
    pw_valid = verify_password(password, pw_hash)
    if user is None or not user.is_active or not pw_valid:
        raise InvalidCredentialsError

    token = create_access_token(user.id, user.username)
    return token, user


async def get_current_user(repo: UserRepository, user_id: UUID) -> User:
    user = await repo.get_or_none(id=user_id)
    if user is None or not user.is_active:
        raise InvalidTokenError
    return user
