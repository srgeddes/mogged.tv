from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from auth.dependencies import get_current_user
from core.exceptions import NotFoundError, PermissionDeniedError
from organizations.dependencies import get_organization_member_repository
from organizations.repository import OrganizationMemberRepository
from users.models import User

from . import service
from .dependencies import get_friend_request_repository, get_friendship_repository
from .exceptions import AlreadyFriendsError, CannotFriendSelfError, FriendRequestExistsError
from .repository import FriendRequestRepository, FriendshipRepository
from .schemas import FriendRequestResponse, FriendResponse, SendFriendRequestBody

router = APIRouter(prefix="/friends", tags=["friends"])


def _request_response(req: object) -> FriendRequestResponse:
    resp = FriendRequestResponse.model_validate(req, from_attributes=True)
    from_user = getattr(req, "from_user", None)
    to_user = getattr(req, "to_user", None)
    updates: dict = {}
    if from_user is not None:
        updates["from_username"] = from_user.username
        updates["from_display_name"] = from_user.display_name
        updates["from_avatar_url"] = from_user.avatar_url
    if to_user is not None:
        updates["to_username"] = to_user.username
        updates["to_display_name"] = to_user.display_name
        updates["to_avatar_url"] = to_user.avatar_url
    if updates:
        resp = resp.model_copy(update=updates)
    return resp


@router.get("", response_model=list[FriendResponse])
async def list_friends(
    current_user: Annotated[User, Depends(get_current_user)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> list[FriendResponse]:
    return await service.list_friends(friendship_repo, org_member_repo, user_id=current_user.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
) -> None:
    try:
        await service.remove_friend(
            friendship_repo,
            user_id=current_user.id,
            friend_user_id=user_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get("/requests/incoming", response_model=list[FriendRequestResponse])
async def incoming_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    request_repo: Annotated[FriendRequestRepository, Depends(get_friend_request_repository)],
) -> list[FriendRequestResponse]:
    requests = await service.list_pending_incoming(request_repo, user_id=current_user.id)
    return [_request_response(r) for r in requests]


@router.get("/requests/outgoing", response_model=list[FriendRequestResponse])
async def outgoing_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    request_repo: Annotated[FriendRequestRepository, Depends(get_friend_request_repository)],
) -> list[FriendRequestResponse]:
    requests = await service.list_pending_outgoing(request_repo, user_id=current_user.id)
    return [_request_response(r) for r in requests]


@router.post("/requests", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
async def send_request(
    body: SendFriendRequestBody,
    current_user: Annotated[User, Depends(get_current_user)],
    request_repo: Annotated[FriendRequestRepository, Depends(get_friend_request_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
) -> FriendRequestResponse:
    try:
        req = await service.send_request(
            request_repo, friendship_repo, from_user_id=current_user.id, to_user_id=body.to_user_id
        )
    except CannotFriendSelfError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except AlreadyFriendsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except FriendRequestExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    return FriendRequestResponse.model_validate(req, from_attributes=True)


@router.post("/requests/{request_id}/accept", response_model=FriendResponse)
async def accept_request(
    request_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    request_repo: Annotated[FriendRequestRepository, Depends(get_friend_request_repository)],
    friendship_repo: Annotated[FriendshipRepository, Depends(get_friendship_repository)],
    org_member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> FriendResponse:
    try:
        friendship = await service.accept_request(
            request_repo, friendship_repo, request_id=request_id, user_id=current_user.id
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc

    friends = await service.list_friends(friendship_repo, org_member_repo, user_id=current_user.id)
    friend_user_id = (
        friendship.user_b_id if friendship.user_a_id == current_user.id else friendship.user_a_id
    )
    for f in friends:
        if f.user_id == friend_user_id:
            return f
    return FriendResponse(user_id=friend_user_id, username="", display_name=None, avatar_url=None)


@router.post("/requests/{request_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_request(
    request_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    request_repo: Annotated[FriendRequestRepository, Depends(get_friend_request_repository)],
) -> None:
    try:
        await service.decline_request(request_repo, request_id=request_id, user_id=current_user.id)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
    request_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    request_repo: Annotated[FriendRequestRepository, Depends(get_friend_request_repository)],
) -> None:
    try:
        await service.cancel_request(request_repo, request_id=request_id, user_id=current_user.id)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
