from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, SoftDeleteMixin, TimestampMixin, created_at_col, uuid_pk

if TYPE_CHECKING:
    from users.models import User


class StreamAccessLevel(enum.StrEnum):
    PUBLIC = "public"
    FRIENDS = "friends"
    ORG_ONLY = "org_only"
    LINK_ONLY = "link_only"


class StreamStatus(enum.StrEnum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"


class ParticipantRole(enum.StrEnum):
    HOST = "host"
    MODERATOR = "moderator"
    VIEWER = "viewer"


class MessageType(enum.StrEnum):
    TEXT = "text"
    EMOTE = "emote"
    SYSTEM = "system"
    AURA_GIFT = "aura_gift"


class Stream(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "streams"
    __table_args__ = (
        Index("ix_streams_host_id", "host_id"),
        Index("ix_streams_status", "status"),
        Index("ix_streams_started_at", "started_at"),
    )

    id: Mapped[uuid_pk]
    host_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[StreamStatus] = mapped_column(
        Enum(StreamStatus, name="stream_status"), default=StreamStatus.SCHEDULED
    )
    room_name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_recording: Mapped[bool] = mapped_column(Boolean, default=False)
    recording_url: Mapped[str | None] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    access_level: Mapped[StreamAccessLevel] = mapped_column(
        Enum(StreamAccessLevel, name="stream_access_level"), default=StreamAccessLevel.PUBLIC
    )
    org_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    aura_pool: Mapped[int] = mapped_column(Integer, default=0)
    max_viewers: Mapped[int | None] = mapped_column(Integer)

    host: Mapped[User] = relationship(
        "User", back_populates="streams", foreign_keys=[host_id], lazy="raise"
    )
    participants: Mapped[list[StreamParticipant]] = relationship(
        "StreamParticipant", back_populates="stream", lazy="raise"
    )
    invite_links: Mapped[list[StreamInviteLink]] = relationship(
        "StreamInviteLink", back_populates="stream", lazy="raise"
    )
    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage", back_populates="stream", lazy="raise"
    )
    metrics: Mapped[StreamMetrics | None] = relationship(
        "StreamMetrics", back_populates="stream", uselist=False, lazy="raise"
    )


class StreamInviteLink(Base, TimestampMixin):
    __tablename__ = "stream_invite_links"
    __table_args__ = (Index("ix_stream_invite_links_stream_id", "stream_id"),)

    id: Mapped[uuid_pk]
    stream_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("streams.id"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    max_uses: Mapped[int | None] = mapped_column(Integer)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    stream: Mapped[Stream] = relationship("Stream", back_populates="invite_links", lazy="raise")
    creator: Mapped[User] = relationship("User", foreign_keys=[created_by], lazy="raise")


class StreamParticipant(Base, TimestampMixin):
    __tablename__ = "stream_participants"
    __table_args__ = (
        Index("ix_stream_participants_stream_id", "stream_id"),
        Index("ix_stream_participants_user_id", "user_id"),
    )

    id: Mapped[uuid_pk]
    stream_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("streams.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    role: Mapped[ParticipantRole] = mapped_column(Enum(ParticipantRole, name="participant_role"))
    invite_link_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("stream_invite_links.id"), nullable=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    aura_received: Mapped[int] = mapped_column(Integer, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    stream: Mapped[Stream] = relationship("Stream", back_populates="participants", lazy="raise")
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], lazy="raise")
    invite_link: Mapped[StreamInviteLink | None] = relationship(
        "StreamInviteLink", foreign_keys=[invite_link_id], lazy="raise"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_stream_created", "stream_id", "created_at"),
        Index("ix_chat_messages_user_id", "user_id"),
    )

    id: Mapped[uuid_pk]
    stream_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("streams.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type"), default=MessageType.TEXT
    )
    reply_to_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chat_messages.id"), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[created_at_col]

    stream: Mapped[Stream] = relationship("Stream", back_populates="messages", lazy="raise")
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], lazy="raise")
    reply_to: Mapped[ChatMessage | None] = relationship(
        "ChatMessage", remote_side="ChatMessage.id", foreign_keys=[reply_to_id], lazy="raise"
    )


class Emote(Base, TimestampMixin):
    __tablename__ = "emotes"
    __table_args__ = (
        Index("ix_emotes_created_by", "created_by"),
        Index("ix_emotes_is_global", "is_global"),
    )

    id: Mapped[uuid_pk]
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str] = mapped_column(String(500))
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)
    is_animated: Mapped[bool] = mapped_column(Boolean, default=False)

    creator: Mapped[User | None] = relationship("User", foreign_keys=[created_by], lazy="raise")


class StreamMetrics(Base):
    __tablename__ = "stream_metrics"

    id: Mapped[uuid_pk]
    stream_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("streams.id"), unique=True, index=True)
    peak_viewers: Mapped[int] = mapped_column(Integer, default=0)
    total_unique_viewers: Mapped[int] = mapped_column(Integer, default=0)
    avg_viewers: Mapped[float] = mapped_column(Float, default=0.0)
    total_messages: Mapped[int] = mapped_column(Integer, default=0)
    total_emotes_used: Mapped[int] = mapped_column(Integer, default=0)
    total_aura_distributed: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    top_chatter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    most_used_emote_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("emotes.id"), nullable=True
    )
    created_at: Mapped[created_at_col]

    stream: Mapped[Stream] = relationship("Stream", back_populates="metrics", lazy="raise")
    top_chatter: Mapped[User | None] = relationship(
        "User", foreign_keys=[top_chatter_id], lazy="raise"
    )
    most_used_emote: Mapped[Emote | None] = relationship(
        "Emote", foreign_keys=[most_used_emote_id], lazy="raise"
    )
