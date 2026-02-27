from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

from .repository import FriendRequestRepository, FriendshipRepository


async def get_friend_request_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> FriendRequestRepository:
    return FriendRequestRepository(session)


async def get_friendship_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> FriendshipRepository:
    return FriendshipRepository(session)
