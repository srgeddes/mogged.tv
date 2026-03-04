from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user, get_optional_user
from core.config import settings
from core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from friends.dependencies import get_friendship_repository
from friends.repository import FriendshipRepository
from organizations.dependencies import get_organization_member_repository
from organizations.repository import OrganizationMemberRepository
from users.dependencies import get_user_repository
from users.models import User
from users.repository import UserRepository

from . import service
from .dependencies import (
    get_invite_link_repository,
    get_participant_repository,
    get_stream_repository,
)
from .repository import StreamInviteLinkRepository, StreamParticipantRepository, StreamRepository
from .schemas import (
    CreateInviteLinkRequest,
    CreateStreamRequest,
    InviteLinkResponse,
    JoinStreamResponse,
    StartStreamResponse,
    StreamResponse,
)

router = APIRouter(prefix="/streams", tags=["streams"])


def _stream_response(stream: object) -> StreamResponse:
    resp = StreamResponse.model_validate(stream, from_attributes=True)
    host = getattr(stream, "host", None)
    if host is not None:
        resp = resp.model_copy(
            update={
                "host_username": host.username,
                "host_display_name": host.display_name,
                "host_avatar_url": host.avatar_url,
            }
        )
    return resp


@router.post("", response_model=StreamResponse, status_code=status.HTTP_201_CREATED)
async def create_stream(
    body: CreateStreamRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> StreamResponse:
    try:
        stream = await service.create_stream(
            stream_repo,
            host_id=current_user.id,
            title=body.title,
            description=body.description,
            access_level=body.access_level,
            org_id=body.org_id,
            scheduled_at=body.scheduled_at,
            org_member_repo=org_member_repo,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return StreamResponse.model_validate(stream, from_attributes=True)


@router.get("/live", response_model=list[StreamResponse])
async def list_live_streams(
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> list[StreamResponse]:
    streams = await service.list_live_streams_for_user(
        stream_repo, friendship_repo, org_member_repo, user_id=current_user.id
    )
    return [_stream_response(s) for s in streams]


@router.get("/recent", response_model=list[StreamResponse])
async def list_recent_streams(
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> list[StreamResponse]:
    streams = await service.list_recent_streams(
        stream_repo, friendship_repo, org_member_repo, user_id=current_user.id, limit=limit
    )
    return [_stream_response(s) for s in streams]


@router.get("/live/u/{username}", response_model=StreamResponse | None)
async def get_live_stream_by_username(
    username: str,
    current_user: Annotated[User | None, Depends(get_optional_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> StreamResponse | None:
    stream = await service.get_live_stream_by_username(
        stream_repo,
        user_repo,
        friendship_repo,
        org_member_repo,
        username=username,
        viewer_id=current_user.id if current_user else None,
    )
    if stream is None:
        return None
    return _stream_response(stream)


@router.get("/live/u/{username}/{slug}", response_model=StreamResponse | None)
async def get_live_stream_by_slug(
    username: str,
    slug: str,
    current_user: Annotated[User | None, Depends(get_optional_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> StreamResponse | None:
    stream = await service.get_live_stream_by_slug(
        stream_repo,
        user_repo,
        username=username,
        slug=slug,
    )
    if stream is None:
        return None
    return _stream_response(stream)


@router.get("/{stream_id}", response_model=StreamResponse)
async def get_stream(
    stream_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> StreamResponse:
    try:
        stream = await stream_repo.get(id=stream_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    if not await service.can_view_stream(
        stream, current_user.id, friendship_repo=friendship_repo, org_member_repo=org_member_repo
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stream not found")
    return _stream_response(stream)


@router.post("/{stream_id}/start", response_model=StartStreamResponse)
async def start_stream(
    stream_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
) -> StartStreamResponse:
    try:
        stream, token = await service.start_stream(
            stream_repo,
            stream_id=stream_id,
            host_id=current_user.id,
            host_username=current_user.username,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return StartStreamResponse(
        token=token,
        livekit_url=settings.livekit_url,
        stream=StreamResponse.model_validate(stream, from_attributes=True),
    )


@router.post("/{stream_id}/end", response_model=StreamResponse)
async def end_stream(
    stream_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
) -> StreamResponse:
    try:
        stream = await service.end_stream(stream_repo, stream_id=stream_id, host_id=current_user.id)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return StreamResponse.model_validate(stream, from_attributes=True)


@router.post("/{stream_id}/join", response_model=JoinStreamResponse)
async def join_stream(
    stream_id: UUID,
    current_user: Annotated[User | None, Depends(get_optional_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    participant_repo: Annotated[StreamParticipantRepository, Depends(get_participant_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
    invite_token: Annotated[str | None, Query()] = None,
) -> JoinStreamResponse:
    try:
        stream, token = await service.join_stream(
            stream_repo,
            participant_repo,
            friendship_repo,
            org_member_repo,
            stream_id=stream_id,
            user_id=current_user.id if current_user else None,
            username=current_user.username if current_user else None,
            invite_token=invite_token,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return JoinStreamResponse(
        token=token,
        livekit_url=settings.livekit_url,
        stream=_stream_response(stream),
    )


@router.post(
    "/{stream_id}/invite-links",
    response_model=InviteLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invite_link(
    stream_id: UUID,
    body: CreateInviteLinkRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    stream_repo: Annotated[StreamRepository, Depends(get_stream_repository)],
    invite_link_repo: Annotated[StreamInviteLinkRepository, Depends(get_invite_link_repository)],
) -> InviteLinkResponse:
    try:
        link = await service.create_invite_link(
            stream_repo,
            invite_link_repo,
            stream_id=stream_id,
            host_id=current_user.id,
            max_uses=body.max_uses,
            expires_in_hours=body.expires_in_hours,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    return InviteLinkResponse.model_validate(link, from_attributes=True)
