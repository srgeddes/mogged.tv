from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

from .repository import OrganizationMemberRepository, OrganizationRepository


async def get_organization_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> OrganizationRepository:
    return OrganizationRepository(session)


async def get_organization_member_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> OrganizationMemberRepository:
    return OrganizationMemberRepository(session)
