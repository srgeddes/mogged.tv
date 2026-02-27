from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

from .repository import AuraTransactionRepository, UserRepository, UserStatsRepository


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_aura_transaction_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuraTransactionRepository:
    return AuraTransactionRepository(session)


async def get_user_stats_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserStatsRepository:
    return UserStatsRepository(session)
