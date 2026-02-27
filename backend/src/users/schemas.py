from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)


class UserSearchResult(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None


class UserStatsResponse(BaseModel):
    model_config = {"from_attributes": True}

    total_streams_hosted: int
    total_streams_watched: int
    total_watch_time_seconds: int
    total_stream_time_seconds: int
    total_aura_earned: int
    total_aura_given: int
    total_messages_sent: int
    total_emotes_sent: int
    longest_stream_seconds: int
    biggest_aura_drop: int
