from __future__ import annotations

from datetime import datetime
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


# --- Computed stats schemas ---


class HostingStats(BaseModel):
    model_config = {"from_attributes": True}

    total_streams_hosted: int
    total_stream_time_seconds: int
    avg_stream_duration_seconds: int
    longest_stream_seconds: int
    total_peak_viewers: int
    avg_peak_viewers: float
    last_stream_ended_at: datetime | None


class WatchingStats(BaseModel):
    model_config = {"from_attributes": True}

    total_streams_watched: int
    total_watch_time_seconds: int
    avg_watch_time_seconds: int
    last_watched_at: datetime | None
    favorite_host_username: str | None
    favorite_host_display_name: str | None


class EngagementStats(BaseModel):
    model_config = {"from_attributes": True}

    total_messages_sent: int
    total_emotes_sent: int
    total_aura_earned: int
    total_aura_given: int
    biggest_aura_drop: int


class HostedStreamItem(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    title: str
    started_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int
    max_viewers: int | None


class WatchedStreamItem(BaseModel):
    model_config = {"from_attributes": True}

    stream_id: UUID
    title: str
    host_username: str
    host_display_name: str | None
    joined_at: datetime
    left_at: datetime | None
    watch_time_seconds: int


class UserStatsOverview(BaseModel):
    hosting: HostingStats
    watching: WatchingStats
    engagement: EngagementStats
    hosted_streams: list[HostedStreamItem]
    watched_streams: list[WatchedStreamItem]
