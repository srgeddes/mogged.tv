from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import func, update

from core.repository import BaseRepository, OrderBy, SortDirection

from .models import AuraTransaction, User, UserStats

if TYPE_CHECKING:
    from collections.abc import Sequence


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
