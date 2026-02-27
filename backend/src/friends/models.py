from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from users.models import User


class FriendRequestStatus(enum.StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class FriendRequest(Base, TimestampMixin):
    __tablename__ = "friend_requests"
    __table_args__ = (
        UniqueConstraint("from_user_id", "to_user_id", name="uq_friend_request"),
        Index("ix_friend_requests_from_user_id", "from_user_id"),
        Index("ix_friend_requests_to_user_id", "to_user_id"),
    )

    id: Mapped[uuid_pk]
    from_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[FriendRequestStatus] = mapped_column(
        Enum(FriendRequestStatus, name="friend_request_status"),
        default=FriendRequestStatus.PENDING,
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    from_user: Mapped[User] = relationship("User", foreign_keys=[from_user_id], lazy="raise")
    to_user: Mapped[User] = relationship("User", foreign_keys=[to_user_id], lazy="raise")


class Friendship(Base, TimestampMixin):
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("user_a_id", "user_b_id", name="uq_friendship"),
        Index("ix_friendships_user_a_id", "user_a_id"),
        Index("ix_friendships_user_b_id", "user_b_id"),
    )

    id: Mapped[uuid_pk]
    user_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("friend_requests.id"))

    user_a: Mapped[User] = relationship("User", foreign_keys=[user_a_id], lazy="raise")
    user_b: Mapped[User] = relationship("User", foreign_keys=[user_b_id], lazy="raise")
    request: Mapped[FriendRequest] = relationship(
        "FriendRequest", foreign_keys=[request_id], lazy="raise"
    )
