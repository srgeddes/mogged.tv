from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .models import FriendRequestStatus


class SendFriendRequestBody(BaseModel):
    to_user_id: UUID


class FriendRequestResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    status: FriendRequestStatus
    created_at: datetime
    from_username: str = ""
    from_display_name: str | None = None
    from_avatar_url: str | None = None
    to_username: str = ""
    to_display_name: str | None = None
    to_avatar_url: str | None = None


class FriendResponse(BaseModel):
    user_id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    is_in_shared_org: bool = False
