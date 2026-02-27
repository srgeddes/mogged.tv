from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user
from core.exceptions import AlreadyExistsError, NotFoundError, PermissionDeniedError
from users.models import User

from . import service
from .dependencies import get_organization_member_repository, get_organization_repository
from .exceptions import InsufficientOrgRoleError, NotOrgMemberError
from .repository import OrganizationMemberRepository, OrganizationRepository
from .schemas import (
    AddMemberRequest,
    CreateOrgRequest,
    OrgMemberResponse,
    OrgResponse,
    UpdateMemberRoleRequest,
)

router = APIRouter(prefix="/orgs", tags=["organizations"])


def _org_response(org: object, member_count: int) -> OrgResponse:
    return OrgResponse.model_validate(org, from_attributes=True).model_copy(
        update={"member_count": member_count}
    )


def _member_response(member: object) -> OrgMemberResponse:
    resp = OrgMemberResponse.model_validate(member, from_attributes=True)
    user = getattr(member, "user", None)
    if user is not None:
        resp = resp.model_copy(
            update={
                "username": user.username,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
            }
        )
    return resp


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    body: CreateOrgRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    org_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> OrgResponse:
    try:
        org = await service.create_org(
            org_repo,
            member_repo,
            name=body.name,
            slug=body.slug,
            description=body.description,
            creator_id=current_user.id,
        )
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    return _org_response(org, 1)


@router.get("", response_model=list[OrgResponse])
async def list_my_orgs(
    current_user: Annotated[User, Depends(get_current_user)],
    org_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> list[OrgResponse]:
    results = await service.list_user_orgs(member_repo, org_repo, user_id=current_user.id)
    return [_org_response(org, count) for org, count in results]


@router.get("/{org_id}", response_model=OrgResponse)
async def get_org(
    org_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    org_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> OrgResponse:
    try:
        org, count = await service.get_org_detail(
            org_repo, member_repo, org_id=org_id, user_id=current_user.id
        )
    except NotOrgMemberError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    return _org_response(org, count)


@router.get("/{org_id}/members", response_model=list[OrgMemberResponse])
async def list_members(
    org_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> list[OrgMemberResponse]:
    try:
        members = await service.list_org_members(
            member_repo, org_id=org_id, user_id=current_user.id
        )
    except NotOrgMemberError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    return [_member_response(m) for m in members]


@router.post(
    "/{org_id}/members",
    response_model=OrgMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    org_id: UUID,
    body: AddMemberRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> OrgMemberResponse:
    try:
        member = await service.add_member(
            member_repo, org_id=org_id, actor_id=current_user.id, target_user_id=body.user_id
        )
    except InsufficientOrgRoleError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    return OrgMemberResponse.model_validate(member, from_attributes=True)


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: UUID,
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> None:
    try:
        await service.remove_member(
            member_repo, org_id=org_id, actor_id=current_user.id, target_user_id=user_id
        )
    except (InsufficientOrgRoleError, PermissionDeniedError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.patch("/{org_id}/members/{user_id}/role", response_model=OrgMemberResponse)
async def update_role(
    org_id: UUID,
    user_id: UUID,
    body: UpdateMemberRoleRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
) -> OrgMemberResponse:
    try:
        member = await service.update_member_role(
            member_repo,
            org_id=org_id,
            actor_id=current_user.id,
            target_user_id=user_id,
            new_role=body.role,
        )
    except (InsufficientOrgRoleError, PermissionDeniedError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    return OrgMemberResponse.model_validate(member, from_attributes=True)


@router.get("/{org_id}/members/search", response_model=list[OrgMemberResponse])
async def search_members(
    org_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    member_repo: Annotated[
        OrganizationMemberRepository,
        Depends(get_organization_member_repository),
    ],
    q: Annotated[str, Query(min_length=1, max_length=100)] = "",
) -> list[OrgMemberResponse]:
    try:
        members = await service.search_org_members(
            member_repo, org_id=org_id, user_id=current_user.id, query=q
        )
    except NotOrgMemberError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    return [_member_response(m) for m in members]
