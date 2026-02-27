from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from core.config import settings
from core.exceptions import NotFoundError, PermissionDeniedError, ValidationError

from .models import StreamAccessLevel, StreamStatus

if TYPE_CHECKING:
    from collections.abc import Sequence

    from friends.repository import FriendshipRepository
    from organizations.repository import OrganizationMemberRepository
    from users.repository import UserRepository

    from .models import Stream, StreamInviteLink
    from .repository import (
        StreamInviteLinkRepository,
        StreamParticipantRepository,
        StreamRepository,
    )


def _generate_room_name() -> str:
    return f"mogged-{uuid.uuid4().hex[:12]}"


def _create_livekit_token(
    room_name: str,
    identity: str,
    *,
    name: str = "",
    can_publish: bool = False,
    can_subscribe: bool = True,
) -> str:
    """Generate a LiveKit access token using the livekit-api SDK."""
    from livekit.api import AccessToken, VideoGrants

    token = AccessToken(
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )
    token.identity = identity
    token.name = name
    token.add_grant(
        VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=can_publish,
            can_subscribe=can_subscribe,
        )
    )
    return token.to_jwt()


async def create_stream(
    stream_repo: StreamRepository,
    *,
    host_id: uuid.UUID,
    title: str,
    description: str | None,
    access_level: StreamAccessLevel,
    org_id: uuid.UUID | None,
    scheduled_at: datetime | None,
    org_member_repo: OrganizationMemberRepository | None = None,
) -> Stream:
    if access_level == StreamAccessLevel.ORG_ONLY and org_id is None:
        raise ValidationError("org_id is required when access_level is org_only")

    if (
        access_level == StreamAccessLevel.ORG_ONLY
        and org_id is not None
        and org_member_repo is not None
    ):
        membership = await org_member_repo.get_membership(org_id, host_id)
        if membership is None:
            raise PermissionDeniedError("You must be a member of this organization")

    return await stream_repo.create(
        host_id=host_id,
        title=title,
        description=description,
        access_level=access_level,
        org_id=org_id,
        room_name=_generate_room_name(),
        status=StreamStatus.SCHEDULED,
        scheduled_at=scheduled_at,
    )


async def start_stream(
    stream_repo: StreamRepository,
    *,
    stream_id: uuid.UUID,
    host_id: uuid.UUID,
    host_username: str,
) -> tuple[Stream, str]:
    stream = await stream_repo.get(id=stream_id)
    if stream.host_id != host_id:
        raise PermissionDeniedError("Only the host can start this stream")
    if stream.status == StreamStatus.LIVE:
        raise ValidationError("Stream is already live")
    if stream.status == StreamStatus.ENDED:
        raise ValidationError("Stream has already ended")

    stream = await stream_repo.update(
        stream_id,
        status=StreamStatus.LIVE,
        started_at=datetime.now(UTC),
    )
    token = _create_livekit_token(
        stream.room_name,
        str(host_id),
        name=host_username,
        can_publish=True,
        can_subscribe=True,
    )
    return stream, token


async def end_stream(
    stream_repo: StreamRepository,
    *,
    stream_id: uuid.UUID,
    host_id: uuid.UUID,
) -> Stream:
    stream = await stream_repo.get(id=stream_id)
    if stream.host_id != host_id:
        raise PermissionDeniedError("Only the host can end this stream")
    if stream.status != StreamStatus.LIVE:
        raise ValidationError("Stream is not live")

    return await stream_repo.update(
        stream_id,
        status=StreamStatus.ENDED,
        ended_at=datetime.now(UTC),
    )


async def can_access_stream(
    stream: Stream,
    user_id: uuid.UUID,
    *,
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
    invite_link_repo: StreamInviteLinkRepository,
    invite_token: str | None = None,
) -> bool:
    if stream.host_id == user_id:
        return True

    if stream.access_level == StreamAccessLevel.PUBLIC:
        return True

    if stream.access_level == StreamAccessLevel.FRIENDS:
        return await friendship_repo.are_friends(stream.host_id, user_id)

    if stream.access_level == StreamAccessLevel.ORG_ONLY:
        if stream.org_id is None:
            return False
        membership = await org_member_repo.get_membership(stream.org_id, user_id)
        return membership is not None

    if stream.access_level == StreamAccessLevel.LINK_ONLY:
        if invite_token is None:
            return False
        try:
            link = await invite_link_repo.get_by_token(invite_token)
        except NotFoundError:
            return False
        if not link.is_active or link.stream_id != stream.id:
            return False
        if link.expires_at and link.expires_at < datetime.now(UTC):
            return False
        if link.max_uses and link.use_count >= link.max_uses:
            return False
        await invite_link_repo.increment_use_count(link.id)
        return True

    return False


async def can_view_stream(
    stream: Stream,
    user_id: uuid.UUID,
    *,
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
) -> bool:
    """Check if a user can view stream metadata (no invite link consumption)."""
    if stream.host_id == user_id:
        return True

    if stream.access_level == StreamAccessLevel.PUBLIC:
        return True

    if stream.access_level == StreamAccessLevel.FRIENDS:
        return await friendship_repo.are_friends(stream.host_id, user_id)

    if stream.access_level == StreamAccessLevel.ORG_ONLY:
        if stream.org_id is None:
            return False
        membership = await org_member_repo.get_membership(stream.org_id, user_id)
        return membership is not None

    # LINK_ONLY streams are only visible to the host
    return False


async def join_stream(
    stream_repo: StreamRepository,
    participant_repo: StreamParticipantRepository,
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
    invite_link_repo: StreamInviteLinkRepository,
    *,
    stream_id: uuid.UUID,
    user_id: uuid.UUID,
    username: str,
    invite_token: str | None = None,
) -> tuple[Stream, str]:
    stream = await stream_repo.get(id=stream_id)
    if stream.status != StreamStatus.LIVE:
        raise ValidationError("Stream is not live")

    allowed = await can_access_stream(
        stream,
        user_id,
        friendship_repo=friendship_repo,
        org_member_repo=org_member_repo,
        invite_link_repo=invite_link_repo,
        invite_token=invite_token,
    )
    if not allowed:
        raise PermissionDeniedError("You don't have access to this stream")

    is_host = stream.host_id == user_id
    token = _create_livekit_token(
        stream.room_name,
        str(user_id),
        name=username,
        can_publish=is_host,
        can_subscribe=True,
    )

    existing = await participant_repo.get_or_none(
        stream_id=stream_id, user_id=user_id, left_at__is_null=True
    )
    if existing is None:
        from .models import ParticipantRole

        await participant_repo.create(
            stream_id=stream_id,
            user_id=user_id,
            role=ParticipantRole.HOST if stream.host_id == user_id else ParticipantRole.VIEWER,
            joined_at=datetime.now(UTC),
        )

    return stream, token


async def list_live_streams_for_user(
    stream_repo: StreamRepository,
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
    *,
    user_id: uuid.UUID,
) -> Sequence[Stream]:
    all_live = await stream_repo.list_live()
    visible: list[Stream] = []
    for stream in all_live:
        if stream.host_id == user_id:
            visible.append(stream)
            continue
        if stream.access_level == StreamAccessLevel.PUBLIC:
            visible.append(stream)
            continue
        if stream.access_level == StreamAccessLevel.FRIENDS:
            if await friendship_repo.are_friends(stream.host_id, user_id):
                visible.append(stream)
            continue
        if stream.access_level == StreamAccessLevel.ORG_ONLY and stream.org_id:
            membership = await org_member_repo.get_membership(stream.org_id, user_id)
            if membership is not None:
                visible.append(stream)
            continue
    return visible


async def list_recent_streams(
    stream_repo: StreamRepository,
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
    *,
    user_id: uuid.UUID,
    limit: int = 20,
) -> Sequence[Stream]:
    from core.repository import OrderBy, SortDirection

    # Fetch more than needed so we can filter by visibility
    all_recent = await stream_repo.list(
        status=StreamStatus.ENDED,
        order_by=[OrderBy("ended_at", SortDirection.DESC)],
        limit=limit * 3,
    )
    visible: list[Stream] = []
    for stream in all_recent:
        if len(visible) >= limit:
            break
        if await can_view_stream(
            stream, user_id, friendship_repo=friendship_repo, org_member_repo=org_member_repo
        ):
            visible.append(stream)
    return visible


async def create_invite_link(
    stream_repo: StreamRepository,
    invite_link_repo: StreamInviteLinkRepository,
    *,
    stream_id: uuid.UUID,
    host_id: uuid.UUID,
    max_uses: int | None,
    expires_in_hours: int | None,
) -> StreamInviteLink:
    stream = await stream_repo.get(id=stream_id)
    if stream.host_id != host_id:
        raise PermissionDeniedError("Only the host can create invite links")

    expires_at = None
    if expires_in_hours:
        expires_at = datetime.now(UTC) + timedelta(hours=expires_in_hours)

    return await invite_link_repo.create(
        stream_id=stream_id,
        created_by=host_id,
        token=secrets.token_urlsafe(32),
        max_uses=max_uses,
        expires_at=expires_at,
    )


async def get_live_stream_by_username(
    stream_repo: StreamRepository,
    user_repo: UserRepository,
    friendship_repo: FriendshipRepository,
    org_member_repo: OrganizationMemberRepository,
    *,
    username: str,
    viewer_id: uuid.UUID,
) -> Stream | None:
    from core.exceptions import NotFoundError

    try:
        user = await user_repo.get_by_username(username)
    except NotFoundError:
        return None
    stream = await stream_repo.get_live_by_host_id(user.id)
    if stream is None:
        return None
    if not await can_view_stream(
        stream, viewer_id, friendship_repo=friendship_repo, org_member_repo=org_member_repo
    ):
        return None
    return stream
