from __future__ import annotations

from core.exceptions import MoggedError


class NoQuestionsAvailableError(MoggedError):
    """Raised when a user has exhausted all available questions."""

    def __init__(self) -> None:
        super().__init__("No more questions available. You've answered them all!")


class QuestionAlreadyAnsweredError(MoggedError):
    """Raised when a user tries to answer a question they already answered."""

    def __init__(self) -> None:
        super().__init__("You already answered this question")


class TimerExpiredError(MoggedError):
    """Raised when a user submits an answer after the timer has expired."""

    def __init__(self) -> None:
        super().__init__("Time's up! You ran out of time")
