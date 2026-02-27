from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user
from core.exceptions import NotFoundError
from users.models import User

from . import service
from .dependencies import get_user_repository, get_user_stats_repository
from .repository import UserRepository, UserStatsRepository
from .schemas import UpdateProfileRequest, UserProfileResponse, UserSearchResult, UserStatsResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user, from_attributes=True)


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    body: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserProfileResponse:
    user = await service.update_profile(
        repo,
        user_id=current_user.id,
        display_name=body.display_name,
        bio=body.bio,
        avatar_url=body.avatar_url,
    )
    return UserProfileResponse.model_validate(user, from_attributes=True)


@router.get("/me/stats", response_model=UserStatsResponse | None)
async def get_my_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    stats_repo: Annotated[UserStatsRepository, Depends(get_user_stats_repository)],
) -> UserStatsResponse | None:
    stats = await service.get_user_stats(stats_repo, user_id=current_user.id)
    if stats is None:
        return None
    return UserStatsResponse.model_validate(stats, from_attributes=True)


@router.get("/search", response_model=list[UserSearchResult])
async def search_users(
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    q: Annotated[str, Query(min_length=1, max_length=100)] = "",
) -> list[UserSearchResult]:
    users = await service.search_users(repo, query=q)
    return [UserSearchResult.model_validate(u, from_attributes=True) for u in users]


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserProfileResponse:
    try:
        user = await service.get_profile(repo, user_id=user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    return UserProfileResponse.model_validate(user, from_attributes=True)
