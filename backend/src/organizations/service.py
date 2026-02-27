from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from core.exceptions import AlreadyExistsError, NotFoundError, PermissionDeniedError

from .exceptions import InsufficientOrgRoleError, NotOrgMemberError
from .models import OrganizationMember, OrgRole

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .models import Organization
    from .repository import OrganizationMemberRepository, OrganizationRepository


async def create_org(
    org_repo: OrganizationRepository,
    member_repo: OrganizationMemberRepository,
    *,
    name: str,
    slug: str,
    description: str | None,
    creator_id: UUID,
) -> Organization:
    if await org_repo.name_exists(name):
        raise AlreadyExistsError("Organization", "name", name)
    if await org_repo.slug_exists(slug):
        raise AlreadyExistsError("Organization", "slug", slug)

    org = await org_repo.create(
        name=name,
        slug=slug,
        description=description,
        created_by=creator_id,
    )
    await member_repo.create(
        organization_id=org.id,
        user_id=creator_id,
        role=OrgRole.OWNER,
    )
    return org


async def list_user_orgs(
    member_repo: OrganizationMemberRepository,
    org_repo: OrganizationRepository,
    *,
    user_id: UUID,
) -> list[tuple[Organization, int]]:
    memberships = await member_repo.list_by_user(user_id)
    results: list[tuple[Organization, int]] = []
    for m in memberships:
        org = await org_repo.get(id=m.organization_id)
        count = await member_repo.count(organization_id=m.organization_id)
        results.append((org, count))
    return results


async def get_org_detail(
    org_repo: OrganizationRepository,
    member_repo: OrganizationMemberRepository,
    *,
    org_id: UUID,
    user_id: UUID,
) -> tuple[Organization, int]:
    org = await org_repo.get(id=org_id)
    membership = await member_repo.get_membership(org_id, user_id)
    if membership is None:
        raise NotOrgMemberError
    count = await member_repo.count(organization_id=org_id)
    return org, count


async def list_org_members(
    member_repo: OrganizationMemberRepository,
    *,
    org_id: UUID,
    user_id: UUID,
) -> Sequence[OrganizationMember]:
    membership = await member_repo.get_membership(org_id, user_id)
    if membership is None:
        raise NotOrgMemberError
    return await member_repo.list_by_org(org_id)


async def add_member(
    member_repo: OrganizationMemberRepository,
    *,
    org_id: UUID,
    actor_id: UUID,
    target_user_id: UUID,
) -> OrganizationMember:
    actor = await member_repo.get_membership(org_id, actor_id)
    if actor is None or actor.role not in (OrgRole.OWNER, OrgRole.ADMIN):
        raise InsufficientOrgRoleError("admin")

    existing = await member_repo.get_membership(org_id, target_user_id)
    if existing is not None:
        raise AlreadyExistsError("OrganizationMember", "user_id", str(target_user_id))

    return await member_repo.create(
        organization_id=org_id,
        user_id=target_user_id,
        role=OrgRole.MEMBER,
    )


async def remove_member(
    member_repo: OrganizationMemberRepository,
    *,
    org_id: UUID,
    actor_id: UUID,
    target_user_id: UUID,
) -> None:
    target = await member_repo.get_membership(org_id, target_user_id)
    if target is None:
        raise NotFoundError("OrganizationMember", user_id=str(target_user_id))

    is_self = actor_id == target_user_id
    if is_self:
        if target.role == OrgRole.OWNER:
            raise PermissionDeniedError("Owners cannot leave. Transfer ownership first.")
        await member_repo.delete(target.id, hard=True)
        return

    actor = await member_repo.get_membership(org_id, actor_id)
    if actor is None or actor.role not in (OrgRole.OWNER, OrgRole.ADMIN):
        raise InsufficientOrgRoleError("admin")
    if target.role == OrgRole.OWNER:
        raise PermissionDeniedError("Cannot remove the org owner")

    await member_repo.delete(target.id, hard=True)


async def update_member_role(
    member_repo: OrganizationMemberRepository,
    *,
    org_id: UUID,
    actor_id: UUID,
    target_user_id: UUID,
    new_role: OrgRole,
) -> OrganizationMember:
    actor = await member_repo.get_membership(org_id, actor_id)
    if actor is None or actor.role != OrgRole.OWNER:
        raise InsufficientOrgRoleError("owner")

    target = await member_repo.get_membership(org_id, target_user_id)
    if target is None:
        raise NotFoundError("OrganizationMember", user_id=str(target_user_id))

    if new_role == OrgRole.OWNER:
        raise PermissionDeniedError("Cannot promote to owner. Transfer ownership instead.")

    return await member_repo.update(target.id, role=new_role)


async def search_org_members(
    member_repo: OrganizationMemberRepository,
    *,
    org_id: UUID,
    user_id: UUID,
    query: str,
) -> Sequence[OrganizationMember]:
    membership = await member_repo.get_membership(org_id, user_id)
    if membership is None:
        raise NotOrgMemberError
    return await member_repo.search_members(org_id, query)
