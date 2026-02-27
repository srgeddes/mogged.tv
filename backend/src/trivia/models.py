from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, TimestampMixin, created_at_col, uuid_pk


class Difficulty(enum.StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionSource(enum.StrEnum):
    OPENTDB = "opentdb"
    CUSTOM = "custom"


class TriviaCategory(Base, TimestampMixin):
    __tablename__ = "trivia_categories"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_brain_rot: Mapped[bool] = mapped_column(Boolean, default=False)
    icon: Mapped[str] = mapped_column(String(50))
    question_count: Mapped[int] = mapped_column(Integer, default=0)

    questions: Mapped[list[TriviaQuestion]] = relationship(
        "TriviaQuestion", back_populates="category", lazy="raise"
    )


class TriviaQuestion(Base, TimestampMixin):
    __tablename__ = "trivia_questions"
    __table_args__ = (
        Index("ix_trivia_questions_category_id", "category_id"),
        Index("ix_trivia_questions_difficulty", "difficulty"),
        Index("ix_trivia_questions_is_active", "is_active"),
    )

    id: Mapped[uuid_pk]
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trivia_categories.id"))
    question_text: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(String(500))
    incorrect_answers: Mapped[str] = mapped_column(Text)  # JSON array of strings
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty, name="difficulty"))
    source: Mapped[QuestionSource] = mapped_column(Enum(QuestionSource, name="question_source"))
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped[TriviaCategory] = relationship(
        "TriviaCategory", back_populates="questions", lazy="raise"
    )
    attempts: Mapped[list[UserTriviaAttempt]] = relationship(
        "UserTriviaAttempt", back_populates="question", lazy="raise"
    )


class UserTriviaAttempt(Base):
    __tablename__ = "user_trivia_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_trivia_attempt"),
        Index("ix_user_trivia_attempts_user_id", "user_id"),
        Index("ix_user_trivia_attempts_answered_at", "answered_at"),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trivia_questions.id"))
    selected_answer: Mapped[str] = mapped_column(String(500))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    aura_earned: Mapped[int] = mapped_column(Integer, default=0)
    answered_at: Mapped[created_at_col]

    question: Mapped[TriviaQuestion] = relationship(
        "TriviaQuestion", back_populates="attempts", lazy="raise"
    )
