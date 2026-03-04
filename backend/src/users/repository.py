from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.repository import BaseRepository, OrderBy, SortDirection
from streams.models import (
    ChatMessage,
    MessageType,
    ParticipantRole,
    Stream,
    StreamParticipant,
    StreamStatus,
)

from .models import AuraTransaction, User, UserStats

if TYPE_CHECKING:
    from collections.abc import Sequence


# --- Dataclass return types for StatsQueryRepository ---


@dataclasses.dataclass(frozen=True)
class HostingStatsRow:
    total_streams_hosted: int
    total_stream_time_seconds: int
    avg_stream_duration_seconds: int
    longest_stream_seconds: int
    total_peak_viewers: int
    avg_peak_viewers: float
    last_stream_ended_at: datetime | None


@dataclasses.dataclass(frozen=True)
class WatchingStatsRow:
    total_streams_watched: int
    total_watch_time_seconds: int
    avg_watch_time_seconds: int
    last_watched_at: datetime | None
    favorite_host_username: str | None
    favorite_host_display_name: str | None


@dataclasses.dataclass(frozen=True)
class EngagementStatsRow:
    total_messages_sent: int
    total_emotes_sent: int
    total_aura_earned: int
    total_aura_given: int
    biggest_aura_drop: int


@dataclasses.dataclass(frozen=True)
class HostedStreamRow:
    id: UUID
    title: str
    started_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int
    max_viewers: int | None


@dataclasses.dataclass(frozen=True)
class WatchedStreamRow:
    stream_id: UUID
    title: str
    host_username: str
    host_display_name: str | None
    joined_at: datetime
    left_at: datetime | None
    watch_time_seconds: int


class StatsQueryRepository:
    """Cross-table aggregate queries for computed user stats."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_hosting_stats(self, user_id: UUID) -> HostingStatsRow:
        duration_expr = func.extract("epoch", Stream.ended_at - Stream.started_at)
        stmt = select(
            func.coalesce(func.count(), 0).label("total_streams_hosted"),
            func.coalesce(func.sum(duration_expr), 0).label("total_stream_time_seconds"),
            func.coalesce(func.avg(duration_expr), 0).label("avg_stream_duration_seconds"),
            func.coalesce(func.max(duration_expr), 0).label("longest_stream_seconds"),
            func.coalesce(func.sum(Stream.max_viewers), 0).label("total_peak_viewers"),
            func.coalesce(func.avg(Stream.max_viewers), 0).label("avg_peak_viewers"),
            func.max(Stream.ended_at).label("last_stream_ended_at"),
        ).where(
            Stream.host_id == user_id,
            Stream.status == StreamStatus.ENDED,
            Stream.deleted_at.is_(None),
        )
        row = (await self.session.execute(stmt)).one()
        return HostingStatsRow(
            total_streams_hosted=int(row.total_streams_hosted),
            total_stream_time_seconds=int(row.total_stream_time_seconds),
            avg_stream_duration_seconds=int(row.avg_stream_duration_seconds),
            longest_stream_seconds=int(row.longest_stream_seconds),
            total_peak_viewers=int(row.total_peak_viewers),
            avg_peak_viewers=float(row.avg_peak_viewers),
            last_stream_ended_at=row.last_stream_ended_at,
        )

    async def _get_favorite_host(self, user_id: UUID) -> tuple[str | None, str | None]:
        stmt = (
            select(
                User.username,
                User.display_name,
            )
            .select_from(StreamParticipant)
            .join(Stream, StreamParticipant.stream_id == Stream.id)
            .join(User, Stream.host_id == User.id)
            .where(
                StreamParticipant.user_id == user_id,
                StreamParticipant.role != ParticipantRole.HOST,
            )
            .group_by(User.id, User.username, User.display_name)
            .order_by(func.count().desc())
            .limit(1)
        )
        row = (await self.session.execute(stmt)).first()
        if row is None:
            return None, None
        return row.username, row.display_name

    async def get_watching_stats(self, user_id: UUID) -> WatchingStatsRow:
        watch_time_expr = func.extract(
            "epoch",
            func.coalesce(StreamParticipant.left_at, func.now()) - StreamParticipant.joined_at,
        )
        stmt = select(
            func.coalesce(func.count(StreamParticipant.stream_id.distinct()), 0).label(
                "total_streams_watched"
            ),
            func.coalesce(func.sum(watch_time_expr), 0).label("total_watch_time_seconds"),
            func.coalesce(func.avg(watch_time_expr), 0).label("avg_watch_time_seconds"),
            func.max(StreamParticipant.joined_at).label("last_watched_at"),
        ).where(
            StreamParticipant.user_id == user_id,
            StreamParticipant.role != ParticipantRole.HOST,
        )
        row = (await self.session.execute(stmt)).one()
        fav_username, fav_display_name = await self._get_favorite_host(user_id)
        return WatchingStatsRow(
            total_streams_watched=int(row.total_streams_watched),
            total_watch_time_seconds=int(row.total_watch_time_seconds),
            avg_watch_time_seconds=int(row.avg_watch_time_seconds),
            last_watched_at=row.last_watched_at,
            favorite_host_username=fav_username,
            favorite_host_display_name=fav_display_name,
        )

    async def get_engagement_stats(self, user_id: UUID) -> EngagementStatsRow:
        # Messages
        msg_stmt = select(
            func.coalesce(func.count(), 0).label("total_messages"),
            func.coalesce(
                func.sum(case((ChatMessage.message_type == MessageType.EMOTE, 1), else_=0)), 0
            ).label("total_emotes"),
        ).where(
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted.is_(False),
        )
        msg_row = (await self.session.execute(msg_stmt)).one()

        # Aura earned
        earned_stmt = select(
            func.coalesce(func.sum(AuraTransaction.amount), 0).label("aura_earned"),
        ).where(AuraTransaction.to_user_id == user_id)
        earned_row = (await self.session.execute(earned_stmt)).one()

        # Aura given
        given_stmt = select(
            func.coalesce(func.sum(AuraTransaction.amount), 0).label("aura_given"),
            func.coalesce(func.max(AuraTransaction.amount), 0).label("biggest_drop"),
        ).where(AuraTransaction.from_user_id == user_id)
        given_row = (await self.session.execute(given_stmt)).one()

        return EngagementStatsRow(
            total_messages_sent=int(msg_row.total_messages),
            total_emotes_sent=int(msg_row.total_emotes),
            total_aura_earned=int(earned_row.aura_earned),
            total_aura_given=int(given_row.aura_given),
            biggest_aura_drop=int(given_row.biggest_drop),
        )

    async def get_hosted_stream_history(
        self, user_id: UUID, *, limit: int = 10
    ) -> list[HostedStreamRow]:
        duration_expr = func.extract("epoch", Stream.ended_at - Stream.started_at)
        stmt = (
            select(
                Stream.id,
                Stream.title,
                Stream.started_at,
                Stream.ended_at,
                func.coalesce(duration_expr, 0).label("duration_seconds"),
                Stream.max_viewers,
            )
            .where(
                Stream.host_id == user_id,
                Stream.status == StreamStatus.ENDED,
                Stream.deleted_at.is_(None),
            )
            .order_by(Stream.ended_at.desc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            HostedStreamRow(
                id=r.id,
                title=r.title,
                started_at=r.started_at,
                ended_at=r.ended_at,
                duration_seconds=int(r.duration_seconds),
                max_viewers=r.max_viewers,
            )
            for r in rows
        ]

    async def get_watched_stream_history(
        self, user_id: UUID, *, limit: int = 10
    ) -> list[WatchedStreamRow]:
        watch_time_expr = func.extract(
            "epoch",
            func.coalesce(StreamParticipant.left_at, func.now()) - StreamParticipant.joined_at,
        )
        stmt = (
            select(
                Stream.id.label("stream_id"),
                Stream.title,
                User.username.label("host_username"),
                User.display_name.label("host_display_name"),
                StreamParticipant.joined_at,
                StreamParticipant.left_at,
                func.coalesce(watch_time_expr, 0).label("watch_time_seconds"),
            )
            .select_from(StreamParticipant)
            .join(Stream, StreamParticipant.stream_id == Stream.id)
            .join(User, Stream.host_id == User.id)
            .where(
                StreamParticipant.user_id == user_id,
                StreamParticipant.role != ParticipantRole.HOST,
                Stream.status == StreamStatus.ENDED,
            )
            .order_by(StreamParticipant.joined_at.desc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            WatchedStreamRow(
                stream_id=r.stream_id,
                title=r.title,
                host_username=r.host_username,
                host_display_name=r.host_display_name,
                joined_at=r.joined_at,
                left_at=r.left_at,
                watch_time_seconds=int(r.watch_time_seconds),
            )
            for r in rows
        ]


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_username(self, username: str) -> User:
        return await self.get(username=username)

    async def get_by_email(self, email: str) -> User:
        return await self.get(email=email)

    async def username_exists(self, username: str) -> bool:
        return await self.exists(username=username)

    async def email_exists(self, email: str) -> bool:
        return await self.exists(email=email)

    async def search_by_display_name(self, query: str) -> Sequence[User]:
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        return await self.list(display_name__ilike=f"%{escaped}%")


class AuraTransactionRepository(BaseRepository[AuraTransaction]):
    model = AuraTransaction

    async def list_by_user(self, user_id: Any) -> Sequence[AuraTransaction]:
        """List transactions where user is sender or receiver, newest first."""
        from sqlalchemy import or_

        stmt = self._base_query()
        stmt = stmt.where(
            or_(
                AuraTransaction.from_user_id == user_id,
                AuraTransaction.to_user_id == user_id,
            )
        )
        stmt = self._apply_ordering(stmt, [OrderBy("created_at", SortDirection.DESC)])
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_stream(self, stream_id: Any) -> Sequence[AuraTransaction]:
        return await self.list(
            stream_id=stream_id,
            order_by=[OrderBy("created_at", SortDirection.DESC)],
        )


class UserStatsRepository(BaseRepository[UserStats]):
    model = UserStats

    async def get_by_user(self, user_id: Any) -> UserStats:
        return await self.get(user_id=user_id)

    async def increment_stat(self, user_id: Any, field: str, amount: int = 1) -> None:
        column = self._get_column(field)
        stmt = (
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values({field: column + amount, "updated_at": func.now()})
        )
        await self.session.execute(stmt)
        await self.session.flush()
