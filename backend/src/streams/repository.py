from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import func, update
from sqlalchemy.orm import selectinload

from core.repository import BaseRepository, OrderBy, SortDirection

from .models import (
    ChatMessage,
    Emote,
    Stream,
    StreamInviteLink,
    StreamMetrics,
    StreamParticipant,
    StreamStatus,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class StreamRepository(BaseRepository[Stream]):
    model = Stream

    async def get_by_room_name(self, room_name: str) -> Stream:
        return await self.get(room_name=room_name)

    async def list_live(self) -> Sequence[Stream]:
        return await self.list(
            status=StreamStatus.LIVE,
            order_by=[OrderBy("started_at", SortDirection.DESC)],
        )

    async def list_by_host(self, host_id: Any) -> Sequence[Stream]:
        return await self.list(
            host_id=host_id,
            order_by=[OrderBy("created_at", SortDirection.DESC)],
        )

    async def get_live_by_host_id(self, host_id: Any) -> Stream | None:
        from sqlalchemy import select

        stmt = (
            select(Stream)
            .where(Stream.host_id == host_id, Stream.status == StreamStatus.LIVE)
            .options(selectinload(Stream.host))
        )
        if hasattr(Stream, "deleted_at"):
            stmt = stmt.where(Stream.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class StreamInviteLinkRepository(BaseRepository[StreamInviteLink]):
    model = StreamInviteLink

    async def get_by_token(self, token: str) -> StreamInviteLink:
        return await self.get(token=token)

    async def increment_use_count(self, link_id: Any) -> None:
        stmt = (
            update(StreamInviteLink)
            .where(StreamInviteLink.id == link_id)
            .values(use_count=StreamInviteLink.use_count + 1, updated_at=func.now())
        )
        await self.session.execute(stmt)
        await self.session.flush()


class StreamParticipantRepository(BaseRepository[StreamParticipant]):
    model = StreamParticipant

    async def get_active_in_stream(self, stream_id: Any, user_id: Any) -> StreamParticipant:
        return await self.get(stream_id=stream_id, user_id=user_id, left_at__is_null=True)

    async def list_by_stream(self, stream_id: Any) -> Sequence[StreamParticipant]:
        return await self.list(
            stream_id=stream_id,
            order_by=[OrderBy("joined_at", SortDirection.ASC)],
        )


class ChatMessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage

    async def list_by_stream(
        self,
        stream_id: Any,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ChatMessage]:
        return await self.list(
            stream_id=stream_id,
            is_deleted=False,
            order_by=[OrderBy("created_at", SortDirection.ASC)],
            limit=limit,
            offset=offset,
        )


class EmoteRepository(BaseRepository[Emote]):
    model = Emote

    async def get_by_code(self, code: str) -> Emote:
        return await self.get(code=code)

    async def list_global(self) -> Sequence[Emote]:
        return await self.list(is_global=True, order_by=[OrderBy("code", SortDirection.ASC)])


class StreamMetricsRepository(BaseRepository[StreamMetrics]):
    model = StreamMetrics

    async def get_by_stream(self, stream_id: Any) -> StreamMetrics:
        return await self.get(stream_id=stream_id)
