from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import selectinload

from core.repository import BaseRepository, OrderBy, SortDirection

from .models import TriviaCategory, TriviaQuestion, UserTriviaAttempt

if TYPE_CHECKING:
    from collections.abc import Sequence


class TriviaCategoryRepository(BaseRepository[TriviaCategory]):
    model = TriviaCategory

    async def list_active(self) -> Sequence[TriviaCategory]:
        return await self.list(
            order_by=[OrderBy("name", SortDirection.ASC)],
        )

    async def get_by_slug(self, slug: str) -> TriviaCategory:
        return await self.get(slug=slug)


class TriviaQuestionRepository(BaseRepository[TriviaQuestion]):
    model = TriviaQuestion

    async def get_random_unseen(
        self,
        user_id: uuid.UUID,
        *,
        category_id: uuid.UUID | None = None,
        difficulty: str | None = None,
    ) -> TriviaQuestion | None:
        answered_subquery = select(UserTriviaAttempt.question_id).where(
            UserTriviaAttempt.user_id == user_id,
        )

        stmt = (
            select(TriviaQuestion)
            .where(
                TriviaQuestion.is_active.is_(True),
                TriviaQuestion.id.not_in(answered_subquery),
            )
            .options(selectinload(TriviaQuestion.category))
            .order_by(func.random())
            .limit(1)
        )

        if category_id is not None:
            stmt = stmt.where(TriviaQuestion.category_id == category_id)
        if difficulty is not None:
            stmt = stmt.where(TriviaQuestion.difficulty == difficulty)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class UserTriviaAttemptRepository(BaseRepository[UserTriviaAttempt]):
    model = UserTriviaAttempt

    async def has_answered(self, user_id: uuid.UUID, question_id: uuid.UUID) -> bool:
        return await self.exists(user_id=user_id, question_id=question_id)

    async def list_recent(
        self, user_id: uuid.UUID, *, limit: int = 20
    ) -> Sequence[UserTriviaAttempt]:
        return await self.list(
            user_id=user_id,
            order_by=[OrderBy("answered_at", SortDirection.DESC)],
            limit=limit,
        )

    async def get_stats(self, user_id: uuid.UUID) -> dict[str, Any]:
        stmt = select(
            func.count().label("total_answered"),
            func.sum(func.cast(UserTriviaAttempt.is_correct, Integer)).label("total_correct"),
            func.coalesce(func.sum(UserTriviaAttempt.aura_earned), 0).label("total_aura_earned"),
        ).where(UserTriviaAttempt.user_id == user_id)

        result = await self.session.execute(stmt)
        row = result.one()
        total_answered = row.total_answered or 0
        total_correct = row.total_correct or 0
        total_aura = row.total_aura_earned or 0

        return {
            "total_answered": total_answered,
            "total_correct": total_correct,
            "accuracy_percent": round(total_correct / total_answered * 100, 1)
            if total_answered > 0
            else 0.0,
            "total_aura_earned": total_aura,
        }

    async def get_current_streak(self, user_id: uuid.UUID) -> int:
        stmt = (
            select(UserTriviaAttempt.is_correct)
            .where(UserTriviaAttempt.user_id == user_id)
            .order_by(UserTriviaAttempt.answered_at.desc())
            .limit(100)
        )
        result = await self.session.execute(stmt)
        streak = 0
        for (is_correct,) in result:
            if is_correct:
                streak += 1
            else:
                break
        return streak
