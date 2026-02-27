from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user
from users.dependencies import get_aura_transaction_repository, get_user_repository
from users.models import User
from users.repository import AuraTransactionRepository, UserRepository

from . import service
from .dependencies import (
    get_trivia_attempt_repository,
    get_trivia_category_repository,
    get_trivia_question_repository,
)
from .exceptions import (
    NoQuestionsAvailableError,
    QuestionAlreadyAnsweredError,
)
from .repository import (
    TriviaCategoryRepository,
    TriviaQuestionRepository,
    UserTriviaAttemptRepository,
)
from .schemas import (
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TriviaCategoryResponse,
    TriviaQuestionResponse,
    TriviaStatsResponse,
)

router = APIRouter(prefix="/trivia", tags=["trivia"])


@router.get("/categories", response_model=list[TriviaCategoryResponse])
async def list_categories(
    current_user: Annotated[User, Depends(get_current_user)],
    category_repo: Annotated[TriviaCategoryRepository, Depends(get_trivia_category_repository)],
) -> list[TriviaCategoryResponse]:
    categories = await service.list_categories(category_repo)
    return [TriviaCategoryResponse.model_validate(c, from_attributes=True) for c in categories]


@router.get("/question", response_model=TriviaQuestionResponse)
async def get_question(
    current_user: Annotated[User, Depends(get_current_user)],
    question_repo: Annotated[TriviaQuestionRepository, Depends(get_trivia_question_repository)],
    category_repo: Annotated[TriviaCategoryRepository, Depends(get_trivia_category_repository)],
    category: Annotated[str | None, Query()] = None,
) -> TriviaQuestionResponse:
    try:
        return await service.get_random_question(
            question_repo,
            category_repo,
            current_user.id,
            category_slug=category,
        )
    except NoQuestionsAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc


@router.post("/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    body: SubmitAnswerRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    question_repo: Annotated[TriviaQuestionRepository, Depends(get_trivia_question_repository)],
    attempt_repo: Annotated[UserTriviaAttemptRepository, Depends(get_trivia_attempt_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    aura_repo: Annotated[AuraTransactionRepository, Depends(get_aura_transaction_repository)],
) -> SubmitAnswerResponse:
    try:
        return await service.submit_answer(
            question_repo,
            attempt_repo,
            user_repo,
            aura_repo,
            current_user.id,
            body.question_id,
            body.selected_answer,
        )
    except QuestionAlreadyAnsweredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc


@router.get("/stats", response_model=TriviaStatsResponse)
async def get_trivia_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    attempt_repo: Annotated[UserTriviaAttemptRepository, Depends(get_trivia_attempt_repository)],
) -> TriviaStatsResponse:
    return await service.get_trivia_stats(attempt_repo, current_user.id)
