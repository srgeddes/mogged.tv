from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from core.exceptions import NotFoundError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .models import User, UserStats
    from .repository import UserRepository, UserStatsRepository


async def get_profile(repo: UserRepository, *, user_id: UUID) -> User:
    user = await repo.get_or_none(id=user_id)
    if user is None or not user.is_active:
        raise NotFoundError("User", id=str(user_id))
    return user


async def update_profile(
    repo: UserRepository,
    *,
    user_id: UUID,
    display_name: str | None = None,
    bio: str | None = None,
    avatar_url: str | None = None,
) -> User:
    updates: dict = {}
    if display_name is not None:
        updates["display_name"] = display_name
    if bio is not None:
        updates["bio"] = bio
    if avatar_url is not None:
        updates["avatar_url"] = avatar_url
    if not updates:
        return await repo.get(id=user_id)
    return await repo.update(user_id, **updates)


async def search_users(
    repo: UserRepository,
    *,
    query: str,
    limit: int = 20,
) -> Sequence[User]:
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return await repo.list(
        display_name__ilike=f"%{escaped}%",
        limit=limit,
    )


async def get_user_stats(
    stats_repo: UserStatsRepository,
    *,
    user_id: UUID,
) -> UserStats | None:
    return await stats_repo.get_or_none(user_id=user_id)
