from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .models import StreamAccessLevel, StreamStatus


class CreateStreamRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    access_level: StreamAccessLevel = StreamAccessLevel.PUBLIC
    org_id: UUID | None = None
    scheduled_at: datetime | None = None


class StreamResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    host_id: UUID
    title: str
    description: str | None
    status: StreamStatus
    room_name: str
    access_level: StreamAccessLevel
    org_id: UUID | None
    scheduled_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    thumbnail_url: str | None
    max_viewers: int | None
    secret_slug: str | None = None
    host_username: str = ""
    host_display_name: str | None = None
    host_avatar_url: str | None = None


class StartStreamResponse(BaseModel):
    token: str
    livekit_url: str
    stream: StreamResponse


class JoinStreamResponse(BaseModel):
    token: str
    livekit_url: str
    stream: StreamResponse


class CreateInviteLinkRequest(BaseModel):
    max_uses: int | None = None
    expires_in_hours: int | None = Field(default=24, ge=1, le=168)


class InviteLinkResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    stream_id: UUID
    token: str
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    is_active: bool
