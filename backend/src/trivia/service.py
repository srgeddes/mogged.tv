from __future__ import annotations

import json
import random
import uuid

from users.models import TransactionType
from users.repository import AuraTransactionRepository, UserRepository

from .constants import AURA_REWARDS, BRAIN_ROT_AURA_REWARD, TIMER_SECONDS
from .exceptions import NoQuestionsAvailableError, QuestionAlreadyAnsweredError
from .models import TriviaCategory, TriviaQuestion
from .repository import (
    TriviaCategoryRepository,
    TriviaQuestionRepository,
    UserTriviaAttemptRepository,
)
from .schemas import SubmitAnswerResponse, TriviaQuestionResponse, TriviaStatsResponse


async def list_categories(
    category_repo: TriviaCategoryRepository,
) -> list[TriviaCategory]:
    categories = await category_repo.list_active()
    return list(categories)


async def get_random_question(
    question_repo: TriviaQuestionRepository,
    category_repo: TriviaCategoryRepository,
    user_id: uuid.UUID,
    *,
    category_slug: str | None = None,
) -> TriviaQuestionResponse:
    category_id = None
    if category_slug is not None:
        category = await category_repo.get_by_slug(category_slug)
        category_id = category.id

    question = await question_repo.get_random_unseen(user_id, category_id=category_id)
    if question is None:
        raise NoQuestionsAvailableError

    return _build_question_response(question)


async def submit_answer(
    question_repo: TriviaQuestionRepository,
    attempt_repo: UserTriviaAttemptRepository,
    user_repo: UserRepository,
    aura_repo: AuraTransactionRepository,
    user_id: uuid.UUID,
    question_id: uuid.UUID,
    selected_answer: str,
) -> SubmitAnswerResponse:
    if await attempt_repo.has_answered(user_id, question_id):
        raise QuestionAlreadyAnsweredError

    question = await question_repo.get(id=question_id)
    is_correct = selected_answer == question.correct_answer

    aura_earned = 0
    if is_correct:
        aura_earned = _calculate_aura(question)

    await attempt_repo.create(
        user_id=user_id,
        question_id=question_id,
        selected_answer=selected_answer,
        is_correct=is_correct,
        aura_earned=aura_earned,
    )

    if aura_earned > 0:
        user = await user_repo.get(id=user_id)
        new_balance = user.aura_balance + aura_earned
        await user_repo.update(user_id, aura_balance=new_balance)
        await aura_repo.create(
            from_user_id=None,
            to_user_id=user_id,
            amount=aura_earned,
            transaction_type=TransactionType.TRIVIA_REWARD,
            note=f"Trivia correct: {question.question_text[:80]}",
        )
    else:
        user = await user_repo.get(id=user_id)
        new_balance = user.aura_balance

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        aura_earned=aura_earned,
        new_aura_balance=new_balance,
    )


async def get_trivia_stats(
    attempt_repo: UserTriviaAttemptRepository,
    user_id: uuid.UUID,
) -> TriviaStatsResponse:
    stats = await attempt_repo.get_stats(user_id)
    streak = await attempt_repo.get_current_streak(user_id)
    return TriviaStatsResponse(
        total_answered=stats["total_answered"],
        total_correct=stats["total_correct"],
        accuracy_percent=stats["accuracy_percent"],
        total_aura_earned=stats["total_aura_earned"],
        current_streak=streak,
    )


def _calculate_aura(question: TriviaQuestion) -> int:
    # Load the category relationship — it should be eagerly loaded
    # when the question was fetched, but fall back to difficulty-based reward.
    try:
        if question.category.is_brain_rot:
            return BRAIN_ROT_AURA_REWARD
    except Exception:
        pass
    return AURA_REWARDS.get(question.difficulty.value, 10)


def _build_question_response(question: TriviaQuestion) -> TriviaQuestionResponse:
    incorrect = json.loads(question.incorrect_answers)
    answers = [question.correct_answer, *incorrect]
    random.shuffle(answers)

    return TriviaQuestionResponse(
        id=question.id,
        category_name=question.category.name,
        category_slug=question.category.slug,
        is_brain_rot=question.category.is_brain_rot,
        question_text=question.question_text,
        difficulty=question.difficulty.value,
        answers=answers,
        timer_seconds=TIMER_SECONDS,
    )
