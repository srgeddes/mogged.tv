from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from core.exceptions import NotFoundError, PermissionDeniedError

from .exceptions import AlreadyFriendsError, CannotFriendSelfError, FriendRequestExistsError
from .models import FriendRequest, FriendRequestStatus

if TYPE_CHECKING:
    from collections.abc import Sequence

    from organizations.repository import OrganizationMemberRepository

    from .models import Friendship
    from .repository import FriendRequestRepository, FriendshipRepository
    from .schemas import FriendResponse


async def send_request(
    request_repo: FriendRequestRepository,
    friendship_repo: FriendshipRepository,
    *,
    from_user_id: UUID,
    to_user_id: UUID,
) -> FriendRequest:
    if from_user_id == to_user_id:
        raise CannotFriendSelfError

    if await friendship_repo.are_friends(from_user_id, to_user_id):
        raise AlreadyFriendsError

    existing = await request_repo.get_between(from_user_id, to_user_id)
    if existing is not None:
        raise FriendRequestExistsError

    return await request_repo.create(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        status=FriendRequestStatus.PENDING,
    )


async def accept_request(
    request_repo: FriendRequestRepository,
    friendship_repo: FriendshipRepository,
    *,
    request_id: UUID,
    user_id: UUID,
) -> Friendship:
    req = await request_repo.get(id=request_id)

    if req.to_user_id != user_id:
        raise PermissionDeniedError("Only the recipient can accept a friend request")

    if req.status != FriendRequestStatus.PENDING:
        raise PermissionDeniedError("This request has already been responded to")

    await request_repo.update(
        req.id,
        status=FriendRequestStatus.ACCEPTED,
        responded_at=datetime.now(UTC),
    )

    a, b = sorted([req.from_user_id, req.to_user_id], key=str)
    return await friendship_repo.create(
        user_a_id=a,
        user_b_id=b,
        request_id=req.id,
    )


async def decline_request(
    request_repo: FriendRequestRepository,
    *,
    request_id: UUID,
    user_id: UUID,
) -> None:
    req = await request_repo.get(id=request_id)

    if req.to_user_id != user_id:
        raise PermissionDeniedError("Only the recipient can decline a friend request")

    if req.status != FriendRequestStatus.PENDING:
        raise PermissionDeniedError("This request has already been responded to")

    await request_repo.update(
        req.id,
        status=FriendRequestStatus.DECLINED,
        responded_at=datetime.now(UTC),
    )


async def cancel_request(
    request_repo: FriendRequestRepository,
    *,
    request_id: UUID,
    user_id: UUID,
) -> None:
    req = await request_repo.get(id=request_id)

    if req.from_user_id != user_id:
        raise PermissionDeniedError("Only the sender can cancel a friend request")

    if req.status != FriendRequestStatus.PENDING:
        raise PermissionDeniedError("This request has already been responded to")

    await request_repo.delete(req.id, hard=True)


async def remove_friend(
    friendship_repo: FriendshipRepository,
    *,
    user_id: UUID,
    friend_user_id: UUID,
) -> None:
    friendship = await friendship_repo.get_friendship(user_id, friend_user_id)
    if friendship is None:
        raise NotFoundError("Friendship", friend_user_id=str(friend_user_id))

    await friendship_repo.delete(friendship.id, hard=True)


async def list_friends(
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
    *,
    user_id: UUID,
) -> list[FriendResponse]:
    from .schemas import FriendResponse

    friendships = await friendship_repo.list_friends(user_id)
    shared_org_user_ids = await org_member_repo.get_shared_org_user_ids(user_id)

    results: list[FriendResponse] = []
    for f in friendships:
        friend = f.user_b if f.user_a_id == user_id else f.user_a
        results.append(
            FriendResponse(
                user_id=friend.id,
                username=friend.username,
                display_name=friend.display_name,
                avatar_url=friend.avatar_url,
                is_in_shared_org=friend.id in shared_org_user_ids,
            )
        )
    return results


async def list_pending_incoming(
    request_repo: FriendRequestRepository,
    *,
    user_id: UUID,
) -> Sequence[FriendRequest]:
    return await request_repo.list_incoming(user_id)


async def list_pending_outgoing(
    request_repo: FriendRequestRepository,
    *,
    user_id: UUID,
) -> Sequence[FriendRequest]:
    return await request_repo.list_outgoing(user_id)
