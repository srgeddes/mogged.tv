from __future__ import annotations

import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", v):
            msg = "Username may only contain letters, numbers, hyphens, and underscores"
            raise ValueError(msg)
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    username: str
    email: str
    display_name: str | None
    avatar_url: str | None
    is_active: bool


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
