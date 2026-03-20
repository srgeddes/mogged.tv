from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_MIN_JWT_SECRET_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "mogged.tv"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mogged"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # LiveKit
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # Auth
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS — accepts comma-separated string or JSON array
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # S3
    s3_bucket: str = "mogged-recordings"

    @model_validator(mode="after")
    def _validate_jwt_secret(self) -> Settings:
        if len(self.jwt_secret_key) < _MIN_JWT_SECRET_LENGTH:
            msg = (
                f"JWT_SECRET_KEY must be at least {_MIN_JWT_SECRET_LENGTH} characters, "
                f"got {len(self.jwt_secret_key)}"
            )
            raise ValueError(msg)
        return self


settings = Settings()
