"""
Tests for /api/auth endpoints:
  POST /api/auth/register
  POST /api/auth/login
  GET  /api/auth/me
"""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_user


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success(self, client: TestClient):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["user"]["username"] == "alice"
        assert "password" not in body["user"]

    def test_register_duplicate_email(self, client: TestClient):
        payload = {
            "username": "bob",
            "email": "bob@example.com",
            "password": "secret123",
        }
        client.post("/api/auth/register", json=payload)  # first — OK
        resp = client.post("/api/auth/register", json={**payload, "username": "bob2"})
        assert resp.status_code == 409

    def test_register_sets_cookie(self, client: TestClient):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "cookie_user",
                "email": "cookie@example.com",
                "password": "cookiepass",
            },
        )
        assert resp.status_code == 201
        assert "access_token" in client.cookies


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self, client: TestClient):
        register_user(client, "charlie", "charlie@example.com", "mypassword")
        resp = client.post(
            "/api/auth/login",
            json={"email": "charlie@example.com", "password": "mypassword"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["user"]["username"] == "charlie"

    def test_login_wrong_password(self, client: TestClient):
        register_user(client, "dave", "dave@example.com", "rightpass")
        resp = client.post(
            "/api/auth/login",
            json={"email": "dave@example.com", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    def test_login_unknown_email(self, client: TestClient):
        resp = client.post(
            "/api/auth/login",
            json={"email": "ghost@example.com", "password": "whatever"},
        )
        assert resp.status_code == 401

    def test_login_sets_cookie(self, client: TestClient):
        register_user(client, "eve", "eve@example.com", "evepass")
        resp = client.post(
            "/api/auth/login",
            json={"email": "eve@example.com", "password": "evepass"},
        )
        assert resp.status_code == 200
        assert "access_token" in client.cookies


# ---------------------------------------------------------------------------
# /auth/me
# ---------------------------------------------------------------------------

class TestMe:
    def test_me_with_valid_token(self, client: TestClient):
        body = register_user(client, "frank", "frank@example.com", "frankpass")
        token = body["access_token"]
        resp = client.get("/api/auth/me", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "frank"

    def test_me_without_token(self, client: TestClient):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_with_invalid_token(self, client: TestClient):
        resp = client.get("/api/auth/me", headers=auth_headers("bad.token.here"))
        assert resp.status_code == 401
