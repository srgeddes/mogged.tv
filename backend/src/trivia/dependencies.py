from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

from .repository import (
    TriviaCategoryRepository,
    TriviaQuestionRepository,
    UserTriviaAttemptRepository,
)


async def get_trivia_category_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TriviaCategoryRepository:
    return TriviaCategoryRepository(session)


async def get_trivia_question_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TriviaQuestionRepository:
    return TriviaQuestionRepository(session)


async def get_trivia_attempt_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserTriviaAttemptRepository:
    return UserTriviaAttemptRepository(session)
