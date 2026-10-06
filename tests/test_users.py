"""
Tests for /api/users endpoints:
  GET  /api/users/me
  GET  /api/users/{id}
  GET  /api/users/
  POST /api/users/{id}/follow
  DELETE /api/users/{id}/follow
"""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_two_users(client: TestClient) -> tuple[str, str, str, str]:
    """Register userA and userB; return (token_a, id_a, token_b, id_b)."""
    a = register_user(client, "userA", "a@example.com", "passA")
    b = register_user(client, "userB", "b@example.com", "passB")
    return a["access_token"], a["user"]["user_id"], b["access_token"], b["user"]["user_id"]


# ---------------------------------------------------------------------------
# Profile endpoints
# ---------------------------------------------------------------------------

class TestUserProfile:
    def test_get_my_profile(self, client: TestClient):
        body = register_user(client, "grace", "grace@example.com", "gracepass")
        token = body["access_token"]
        resp = client.get("/api/users/me", headers=auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "grace"
        assert "followers_count" in data
        assert "following_count" in data

    def test_get_profile_by_id(self, client: TestClient):
        body = register_user(client, "henry", "henry@example.com", "henrypass")
        user_id = body["user"]["user_id"]
        token = body["access_token"]
        resp = client.get(f"/api/users/{user_id}", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "henry"

    def test_get_profile_nonexistent_user(self, client: TestClient):
        body = register_user(client, "iris", "iris@example.com", "irispass")
        token = body["access_token"]
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = client.get(f"/api/users/{fake_id}", headers=auth_headers(token))
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# List users
# ---------------------------------------------------------------------------

class TestListUsers:
    def test_list_users_authenticated(self, client: TestClient):
        token_a, _, _, _ = _setup_two_users(client)
        resp = client.get("/api/users/", headers=auth_headers(token_a))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 2

    def test_list_users_unauthenticated(self, client: TestClient):
        resp = client.get("/api/users/")
        assert resp.status_code == 401

    def test_list_users_pagination(self, client: TestClient):
        token_a, _, _, _ = _setup_two_users(client)
        resp = client.get("/api/users/?skip=0&limit=1", headers=auth_headers(token_a))
        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ---------------------------------------------------------------------------
# Follow / Unfollow
# ---------------------------------------------------------------------------

class TestFollowUnfollow:
    def test_follow_user(self, client: TestClient):
        token_a, id_a, _, id_b = _setup_two_users(client)
        resp = client.post(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        assert resp.status_code == 201
        body = resp.json()
        assert body["follower_id"] == id_a
        assert body["followed_id"] == id_b

    def test_follow_updates_followers_count(self, client: TestClient):
        token_a, _, token_b, id_b = _setup_two_users(client)
        client.post(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        profile = client.get(f"/api/users/{id_b}", headers=auth_headers(token_b))
        assert profile.json()["followers_count"] == 1

    def test_follow_self_is_rejected(self, client: TestClient):
        body = register_user(client, "jack", "jack@example.com", "jackpass")
        token = body["access_token"]
        user_id = body["user"]["user_id"]
        resp = client.post(f"/api/users/{user_id}/follow", headers=auth_headers(token))
        assert resp.status_code == 409

    def test_double_follow_is_rejected(self, client: TestClient):
        token_a, _, _, id_b = _setup_two_users(client)
        client.post(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        resp = client.post(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        assert resp.status_code == 409

    def test_unfollow_user(self, client: TestClient):
        token_a, _, token_b, id_b = _setup_two_users(client)
        client.post(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        resp = client.delete(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        assert resp.status_code == 200
        # Followers count back to 0
        profile = client.get(f"/api/users/{id_b}", headers=auth_headers(token_b))
        assert profile.json()["followers_count"] == 0

    def test_unfollow_not_following_is_rejected(self, client: TestClient):
        token_a, _, _, id_b = _setup_two_users(client)
        resp = client.delete(f"/api/users/{id_b}/follow", headers=auth_headers(token_a))
        assert resp.status_code == 404

    def test_follow_requires_auth(self, client: TestClient):
        _, _, _, id_b = _setup_two_users(client)
        # Clear any cookie left by registration before making the unauthenticated call
        client.cookies.clear()
        resp = client.post(f"/api/users/{id_b}/follow")
        assert resp.status_code == 401
