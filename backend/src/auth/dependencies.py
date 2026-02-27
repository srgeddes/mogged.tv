from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from users.dependencies import get_user_repository
from users.models import User
from users.repository import UserRepository

from . import service
from .exceptions import InvalidTokenError

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    if credentials is None:
        raise InvalidTokenError

    from core.security import decode_access_token

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise InvalidTokenError from exc

    return await service.get_current_user(repo, user_id=UUID(payload["sub"]))
