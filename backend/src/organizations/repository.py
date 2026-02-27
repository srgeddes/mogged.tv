from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository, OrderBy, SortDirection

from .models import Organization, OrganizationMember

if TYPE_CHECKING:
    from collections.abc import Sequence


class OrganizationRepository(BaseRepository[Organization]):
    model = Organization

    async def get_by_slug(self, slug: str) -> Organization:
        return await self.get(slug=slug)

    async def slug_exists(self, slug: str) -> bool:
        return await self.exists(slug=slug)

    async def name_exists(self, name: str) -> bool:
        return await self.exists(name=name)


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    model = OrganizationMember

    async def get_membership(self, organization_id: Any, user_id: Any) -> OrganizationMember | None:
        return await self.get_or_none(organization_id=organization_id, user_id=user_id)

    async def list_by_org(self, organization_id: Any) -> Sequence[OrganizationMember]:
        stmt = (
            select(OrganizationMember)
            .options(joinedload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == organization_id)
            .order_by(OrganizationMember.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def list_by_user(self, user_id: Any) -> Sequence[OrganizationMember]:
        return await self.list(
            user_id=user_id,
            order_by=[OrderBy("created_at", SortDirection.DESC)],
        )

    async def search_members(
        self, organization_id: Any, query: str
    ) -> Sequence[OrganizationMember]:
        """Search org members by joined user's display_name or username."""
        from users.models import User

        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        stmt = (
            select(OrganizationMember)
            .join(User, OrganizationMember.user_id == User.id)
            .options(joinedload(OrganizationMember.user))
            .where(
                OrganizationMember.organization_id == organization_id,
                (User.display_name.ilike(pattern)) | (User.username.ilike(pattern)),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_shared_org_user_ids(self, user_id: Any) -> set[Any]:
        """Return set of user_ids that share at least one org with the given user."""
        user_org_ids = await self.list_attribute("organization_id", user_id=user_id)
        if not user_org_ids:
            return set()
        co_members = await self.list(organization_id__in=list(user_org_ids))
        return {m.user_id for m in co_members if m.user_id != user_id}
