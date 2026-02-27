from __future__ import annotations

import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .models import OrgRole


class CreateOrgRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", v):
            msg = "Slug must be lowercase alphanumeric with hyphens only"
            raise ValueError(msg)
        return v


class OrgResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    slug: str
    description: str | None
    avatar_url: str | None
    created_by: UUID
    member_count: int = 0


class OrgMemberResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrgRole
    username: str = ""
    display_name: str | None = None
    avatar_url: str | None = None


class AddMemberRequest(BaseModel):
    user_id: UUID


class UpdateMemberRoleRequest(BaseModel):
    role: OrgRole
