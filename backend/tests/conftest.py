from __future__ import annotations

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-at-least-32-characters-long")

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.database import get_async_session
from core.models import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def _setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _test_session() -> AsyncGenerator[AsyncSession]:
    async with TestSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client():
    # Import here so module-level config doesn't interfere
    from main import app

    app.dependency_overrides[get_async_session] = _test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Sign up a test user and return auth headers."""
    resp = await client.post(
        "/api/auth/signup",
        json={
            "username": "testuser",
            "email": "test@mogged.tv",
            "password": "password123",
            "display_name": "Test User",
        },
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def create_user(
    client: AsyncClient,
    username: str,
    email: str,
) -> tuple[dict[str, str], dict]:
    """Helper: sign up a user, return (headers, user_data)."""
    resp = await client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password": "password123",
            "display_name": username.title(),
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return headers, data["user"]
