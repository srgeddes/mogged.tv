from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

from .repository import (
    ChatMessageRepository,
    EmoteRepository,
    StreamInviteLinkRepository,
    StreamMetricsRepository,
    StreamParticipantRepository,
    StreamRepository,
)


async def get_stream_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StreamRepository:
    return StreamRepository(session)


async def get_invite_link_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StreamInviteLinkRepository:
    return StreamInviteLinkRepository(session)


async def get_participant_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StreamParticipantRepository:
    return StreamParticipantRepository(session)


async def get_chat_message_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ChatMessageRepository:
    return ChatMessageRepository(session)


async def get_emote_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> EmoteRepository:
    return EmoteRepository(session)


async def get_stream_metrics_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StreamMetricsRepository:
    return StreamMetricsRepository(session)
