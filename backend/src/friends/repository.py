from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository

from .models import FriendRequest, FriendRequestStatus, Friendship

if TYPE_CHECKING:
    from collections.abc import Sequence


class FriendRequestRepository(BaseRepository[FriendRequest]):
    model = FriendRequest

    async def get_between(self, user_a_id: Any, user_b_id: Any) -> FriendRequest | None:
        """Find any pending request between two users (either direction)."""
        stmt = select(FriendRequest).where(
            FriendRequest.status == FriendRequestStatus.PENDING,
            or_(
                (FriendRequest.from_user_id == user_a_id) & (FriendRequest.to_user_id == user_b_id),
                (FriendRequest.from_user_id == user_b_id) & (FriendRequest.to_user_id == user_a_id),
            ),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_incoming(self, user_id: Any) -> Sequence[FriendRequest]:
        stmt = (
            select(FriendRequest)
            .options(joinedload(FriendRequest.from_user), joinedload(FriendRequest.to_user))
            .where(
                FriendRequest.to_user_id == user_id,
                FriendRequest.status == FriendRequestStatus.PENDING,
            )
            .order_by(FriendRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def list_outgoing(self, user_id: Any) -> Sequence[FriendRequest]:
        stmt = (
            select(FriendRequest)
            .options(joinedload(FriendRequest.from_user), joinedload(FriendRequest.to_user))
            .where(
                FriendRequest.from_user_id == user_id,
                FriendRequest.status == FriendRequestStatus.PENDING,
            )
            .order_by(FriendRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()


class FriendshipRepository(BaseRepository[Friendship]):
    model = Friendship

    async def get_friendship(self, user_a_id: Any, user_b_id: Any) -> Friendship | None:
        """Find friendship between two users (order-independent)."""
        a, b = sorted([user_a_id, user_b_id], key=str)
        return await self.get_or_none(user_a_id=a, user_b_id=b)

    async def list_friends(self, user_id: Any) -> Sequence[Friendship]:
        stmt = (
            select(Friendship)
            .options(joinedload(Friendship.user_a), joinedload(Friendship.user_b))
            .where(
                or_(
                    Friendship.user_a_id == user_id,
                    Friendship.user_b_id == user_id,
                )
            )
            .order_by(Friendship.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def are_friends(self, user_a_id: Any, user_b_id: Any) -> bool:
        friendship = await self.get_friendship(user_a_id, user_b_id)
        return friendship is not None
