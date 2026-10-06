"""
Tests for /api/posts endpoints:
  POST /api/posts/
  GET  /api/posts/
"""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _token(client: TestClient, username: str, suffix: str = "") -> str:
    body = register_user(client, username, f"{username}{suffix}@example.com", "pass1234")
    return body["access_token"]


# ---------------------------------------------------------------------------
# Create post
# ---------------------------------------------------------------------------

class TestCreatePost:
    def test_create_post_success(self, client: TestClient):
        token = _token(client, "poster1")
        resp = client.post(
            "/api/posts/",
            json={"body": "Hello world!"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["id"].startswith("post_")
        assert body["status"] == "PUBLIC"

    def test_create_post_with_all_fields(self, client: TestClient):
        token = _token(client, "poster2")
        resp = client.post(
            "/api/posts/",
            json={
                "body": "A post with extras",
                "image": "https://example.com/img.png",
                "location": "Cairo",
                "status": "PRIVATE",
            },
            headers=auth_headers(token),
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "PRIVATE"

    def test_create_post_empty_body_rejected(self, client: TestClient):
        token = _token(client, "poster3")
        resp = client.post(
            "/api/posts/",
            json={"body": "   "},
            headers=auth_headers(token),
        )
        assert resp.status_code == 400

    def test_create_post_requires_auth(self, client: TestClient):
        resp = client.post("/api/posts/", json={"body": "No auth"})
        assert resp.status_code == 401

    def test_create_post_missing_body_field(self, client: TestClient):
        token = _token(client, "poster4")
        resp = client.post(
            "/api/posts/",
            json={"image": "https://example.com/img.png"},
            headers=auth_headers(token),
        )
        # The app's custom validation_error_handler maps all Pydantic errors to 400
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Get posts
# ---------------------------------------------------------------------------

class TestGetPosts:
    def test_get_posts_empty(self, client: TestClient):
        token = _token(client, "reader1")
        resp = client.get("/api/posts/", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_posts_after_creating(self, client: TestClient):
        token = _token(client, "reader2")
        client.post("/api/posts/", json={"body": "Post one"}, headers=auth_headers(token))
        client.post("/api/posts/", json={"body": "Post two"}, headers=auth_headers(token))
        resp = client.get("/api/posts/", headers=auth_headers(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_posts_pagination(self, client: TestClient):
        token = _token(client, "reader3")
        for i in range(5):
            client.post("/api/posts/", json={"body": f"Post {i}"}, headers=auth_headers(token))
        resp = client.get("/api/posts/?skip=0&limit=3", headers=auth_headers(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_get_posts_requires_auth(self, client: TestClient):
        resp = client.get("/api/posts/")
        assert resp.status_code == 401

    def test_posts_are_user_scoped(self, client: TestClient):
        """User A's /posts/ should only return their own posts."""
        token_a = _token(client, "scopeA")
        token_b = _token(client, "scopeB")
        client.post("/api/posts/", json={"body": "A's post"}, headers=auth_headers(token_a))
        client.post("/api/posts/", json={"body": "B's post"}, headers=auth_headers(token_b))
        resp = client.get("/api/posts/", headers=auth_headers(token_a))
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"].startswith("post_")
