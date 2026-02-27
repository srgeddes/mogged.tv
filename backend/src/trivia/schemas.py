from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class TriviaCategoryResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    slug: str
    is_brain_rot: bool
    icon: str
    question_count: int


class TriviaQuestionResponse(BaseModel):
    id: UUID
    category_name: str
    category_slug: str
    is_brain_rot: bool
    question_text: str
    difficulty: str
    answers: list[str]
    timer_seconds: int


class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    selected_answer: str


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    aura_earned: int
    new_aura_balance: int


class TriviaStatsResponse(BaseModel):
    total_answered: int
    total_correct: int
    accuracy_percent: float
    total_aura_earned: int
    current_streak: int
