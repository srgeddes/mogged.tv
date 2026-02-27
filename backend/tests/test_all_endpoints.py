"""Smoke tests for every endpoint — verifies routes exist, accept valid
payloads, and return expected status codes against an in-memory SQLite DB."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import AsyncClient
from tests.conftest import create_user

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    resp = await client.post(
        "/api/auth/signup",
        json={
            "username": "newuser",
            "email": "new@mogged.tv",
            "password": "password123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"


@pytest.mark.asyncio
async def test_signup_duplicate_username(client: AsyncClient):
    payload = {
        "username": "dupuser",
        "email": "dup1@mogged.tv",
        "password": "password123",
    }
    await client.post("/api/auth/signup", json=payload)
    resp = await client.post(
        "/api/auth/signup",
        json={**payload, "email": "dup2@mogged.tv"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "username": "loginuser",
            "email": "login@mogged.tv",
            "password": "password123",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "login@mogged.tv", "password": "password123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "username": "badpw",
            "email": "badpw@mogged.tv",
            "password": "password123",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "badpw@mogged.tv", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_auth_me_no_token(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_users_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_users_update_me(client: AsyncClient, auth_headers: dict):
    resp = await client.patch(
        "/api/users/me",
        headers=auth_headers,
        json={"display_name": "Updated Name", "bio": "hello world"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_users_me_stats(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/users/me/stats", headers=auth_headers)
    # Stats may not exist yet — should return 200 with null
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_users_search(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/users/search", headers=auth_headers, params={"q": "test"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_users_get_by_id(client: AsyncClient, auth_headers: dict):
    me = await client.get("/api/users/me", headers=auth_headers)
    user_id = me.json()["id"]
    resp = await client.get(f"/api/users/{user_id}", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_users_get_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(f"/api/users/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Streams
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_stream(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/streams",
        headers=auth_headers,
        json={"title": "Test Stream", "access_level": "public"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Stream"
    assert data["status"] == "scheduled"


@pytest.mark.asyncio
async def test_create_stream_org_only_requires_org_id(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/streams",
        headers=auth_headers,
        json={"title": "Org Stream", "access_level": "org_only"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_stream(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/streams",
        headers=auth_headers,
        json={"title": "Get Test", "access_level": "public"},
    )
    stream_id = create.json()["id"]
    resp = await client.get(f"/api/streams/{stream_id}", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_live_streams(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/streams/live", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_recent_streams(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/streams/recent", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_start_stream(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/streams",
        headers=auth_headers,
        json={"title": "Start Test", "access_level": "public"},
    )
    stream_id = create.json()["id"]

    with patch("streams.service._create_livekit_token", return_value="mock-token"):
        resp = await client.post(f"/api/streams/{stream_id}/start", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["token"] == "mock-token"
    assert data["stream"]["status"] == "live"


@pytest.mark.asyncio
async def test_end_stream(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/streams",
        headers=auth_headers,
        json={"title": "End Test", "access_level": "public"},
    )
    stream_id = create.json()["id"]

    with patch("streams.service._create_livekit_token", return_value="mock-token"):
        await client.post(f"/api/streams/{stream_id}/start", headers=auth_headers)

    resp = await client.post(f"/api/streams/{stream_id}/end", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ended"


@pytest.mark.asyncio
async def test_join_stream(client: AsyncClient):
    host_headers, _ = await create_user(client, "host", "host@mogged.tv")
    viewer_headers, _ = await create_user(client, "viewer", "viewer@mogged.tv")

    create = await client.post(
        "/api/streams",
        headers=host_headers,
        json={"title": "Join Test", "access_level": "public"},
    )
    stream_id = create.json()["id"]

    with patch("streams.service._create_livekit_token", return_value="mock-token"):
        await client.post(f"/api/streams/{stream_id}/start", headers=host_headers)
        resp = await client.post(f"/api/streams/{stream_id}/join", headers=viewer_headers)
    assert resp.status_code == 200
    assert resp.json()["token"] == "mock-token"


@pytest.mark.asyncio
async def test_create_invite_link(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/streams",
        headers=auth_headers,
        json={"title": "Invite Test", "access_level": "link_only"},
    )
    stream_id = create.json()["id"]
    resp = await client.post(
        f"/api/streams/{stream_id}/invite-links",
        headers=auth_headers,
        json={"max_uses": 5, "expires_in_hours": 24},
    )
    assert resp.status_code == 201
    assert "token" in resp.json()


# ---------------------------------------------------------------------------
# Friends
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_friend_request(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice", "alice@mogged.tv")
    _, user_b = await create_user(client, "bob", "bob@mogged.tv")

    resp = await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_accept_friend_request(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice2", "alice2@mogged.tv")
    headers_b, user_b = await create_user(client, "bob2", "bob2@mogged.tv")

    send = await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )
    request_id = send.json()["id"]

    resp = await client.post(f"/api/friends/requests/{request_id}/accept", headers=headers_b)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_decline_friend_request(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice3", "alice3@mogged.tv")
    headers_b, user_b = await create_user(client, "bob3", "bob3@mogged.tv")

    send = await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )
    request_id = send.json()["id"]

    resp = await client.post(f"/api/friends/requests/{request_id}/decline", headers=headers_b)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_cancel_friend_request(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice4", "alice4@mogged.tv")
    _, user_b = await create_user(client, "bob4", "bob4@mogged.tv")

    send = await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )
    request_id = send.json()["id"]

    resp = await client.delete(f"/api/friends/requests/{request_id}", headers=headers_a)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_list_friends(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice5", "alice5@mogged.tv")
    headers_b, user_b = await create_user(client, "bob5", "bob5@mogged.tv")

    send = await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )
    await client.post(f"/api/friends/requests/{send.json()['id']}/accept", headers=headers_b)

    resp = await client.get("/api/friends", headers=headers_a)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_remove_friend(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice6", "alice6@mogged.tv")
    headers_b, user_b = await create_user(client, "bob6", "bob6@mogged.tv")

    send = await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )
    await client.post(f"/api/friends/requests/{send.json()['id']}/accept", headers=headers_b)

    resp = await client.delete(f"/api/friends/{user_b['id']}", headers=headers_a)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_list_incoming_requests(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice7", "alice7@mogged.tv")
    headers_b, user_b = await create_user(client, "bob7", "bob7@mogged.tv")

    await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )

    resp = await client.get("/api/friends/requests/incoming", headers=headers_b)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_list_outgoing_requests(client: AsyncClient):
    headers_a, _ = await create_user(client, "alice8", "alice8@mogged.tv")
    _, user_b = await create_user(client, "bob8", "bob8@mogged.tv")

    await client.post(
        "/api/friends/requests",
        headers=headers_a,
        json={"to_user_id": user_b["id"]},
    )

    resp = await client.get("/api/friends/requests/outgoing", headers=headers_a)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_org(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={
            "name": "Test Org",
            "slug": "test-org",
            "description": "A test organization",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Org"
    assert data["slug"] == "test-org"


@pytest.mark.asyncio
async def test_list_orgs(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "My Org", "slug": "my-org"},
    )
    resp = await client.get("/api/orgs", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_get_org(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "Get Org", "slug": "get-org"},
    )
    org_id = create.json()["id"]
    resp = await client.get(f"/api/orgs/{org_id}", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_org_members(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "Members Org", "slug": "members-org"},
    )
    org_id = create.json()["id"]
    resp = await client.get(f"/api/orgs/{org_id}/members", headers=auth_headers)
    assert resp.status_code == 200
    # Creator should be the first member
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_add_org_member(client: AsyncClient, auth_headers: dict):
    _, user_b = await create_user(client, "orgmember", "orgmember@mogged.tv")

    create = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "Add Org", "slug": "add-org"},
    )
    org_id = create.json()["id"]

    resp = await client.post(
        f"/api/orgs/{org_id}/members",
        headers=auth_headers,
        json={"user_id": user_b["id"]},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_update_member_role(client: AsyncClient, auth_headers: dict):
    _, user_b = await create_user(client, "roleuser", "roleuser@mogged.tv")

    create = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "Role Org", "slug": "role-org"},
    )
    org_id = create.json()["id"]

    await client.post(
        f"/api/orgs/{org_id}/members",
        headers=auth_headers,
        json={"user_id": user_b["id"]},
    )

    resp = await client.patch(
        f"/api/orgs/{org_id}/members/{user_b['id']}/role",
        headers=auth_headers,
        json={"role": "admin"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_remove_org_member(client: AsyncClient, auth_headers: dict):
    headers_b, user_b = await create_user(client, "rmuser", "rmuser@mogged.tv")

    create = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "Remove Org", "slug": "remove-org"},
    )
    org_id = create.json()["id"]

    await client.post(
        f"/api/orgs/{org_id}/members",
        headers=auth_headers,
        json={"user_id": user_b["id"]},
    )

    resp = await client.delete(f"/api/orgs/{org_id}/members/{user_b['id']}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_search_org_members(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/orgs",
        headers=auth_headers,
        json={"name": "Search Org", "slug": "search-org"},
    )
    org_id = create.json()["id"]
    resp = await client.get(
        f"/api/orgs/{org_id}/members/search",
        headers=auth_headers,
        params={"q": "test"},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Unauthenticated access — all protected routes should return 401
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/users/me"),
        ("PATCH", "/api/users/me"),
        ("GET", "/api/streams/live"),
        ("POST", "/api/streams"),
        ("GET", "/api/friends"),
        ("GET", "/api/orgs"),
    ],
)
async def test_unauthenticated_returns_401(client: AsyncClient, method: str, path: str):
    resp = await client.request(method, path)
    assert resp.status_code == 401
