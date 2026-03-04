from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    updated_at_col,
    uuid_pk,
)

if TYPE_CHECKING:
    from streams.models import Stream


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    aura_balance: Mapped[int] = mapped_column(Integer, default=1000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    streams: Mapped[list[Stream]] = relationship(
        "Stream", back_populates="host", foreign_keys="Stream.host_id", lazy="raise"
    )
    stats: Mapped[UserStats | None] = relationship(
        "UserStats", back_populates="user", uselist=False, lazy="raise"
    )


class TransactionType(enum.StrEnum):
    STREAM_REWARD = "stream_reward"
    GIFT = "gift"
    BONUS = "bonus"
    REFUND = "refund"
    TRIVIA_REWARD = "trivia_reward"


class AuraTransaction(Base, TimestampMixin):
    __tablename__ = "aura_transactions"
    __table_args__ = (
        Index("ix_aura_transactions_from_user_id", "from_user_id"),
        Index("ix_aura_transactions_to_user_id", "to_user_id"),
        Index("ix_aura_transactions_stream_id", "stream_id"),
        Index("ix_aura_transactions_created_at", "created_at"),
    )

    id: Mapped[uuid_pk]
    from_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    to_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(Integer)
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type")
    )
    stream_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("streams.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255))

    from_user: Mapped[User | None] = relationship("User", foreign_keys=[from_user_id], lazy="raise")
    to_user: Mapped[User] = relationship("User", foreign_keys=[to_user_id], lazy="raise")


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    total_streams_hosted: Mapped[int] = mapped_column(Integer, default=0)
    total_streams_watched: Mapped[int] = mapped_column(Integer, default=0)
    total_watch_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    total_stream_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    total_aura_earned: Mapped[int] = mapped_column(Integer, default=0)
    total_aura_given: Mapped[int] = mapped_column(Integer, default=0)
    total_messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_emotes_sent: Mapped[int] = mapped_column(Integer, default=0)
    longest_stream_seconds: Mapped[int] = mapped_column(Integer, default=0)
    biggest_aura_drop: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[updated_at_col]

    user: Mapped[User] = relationship("User", back_populates="stats", lazy="raise")
