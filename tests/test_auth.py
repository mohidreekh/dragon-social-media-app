import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_full_auth_and_protected_endpoints():
    # 1. Register User A
    user_a_data = {
        "username": "user_a",
        "email": "user_a@example.com",
        "password": "passwordA123",
        "profile_image": "http://example.com/a.png"
    }
    resp_a = client.post("/api/auth/register", json=user_a_data)
    if resp_a.status_code == 201:
        token_a = resp_a.json()["access_token"]
        user_a_id = resp_a.json()["user"]["user_id"]
    else:
        # Login if user A already exists
        login_resp = client.post("/api/auth/login", json={"email": "user_a@example.com", "password": "passwordA123"})
        token_a = login_resp.json()["access_token"]
        me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_a}"})
        user_a_id = me_resp.json()["user_id"]

    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B
    user_b_data = {
        "username": "user_b",
        "email": "user_b@example.com",
        "password": "passwordB123",
        "profile_image": "http://example.com/b.png"
    }
    resp_b = client.post("/api/auth/register", json=user_b_data)
    if resp_b.status_code == 201:
        token_b = resp_b.json()["access_token"]
        user_b_id = resp_b.json()["user"]["user_id"]
    else:
        login_resp = client.post("/api/auth/login", json={"email": "user_b@example.com", "password": "passwordB123"})
        token_b = login_resp.json()["access_token"]
        me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_b}"})
        user_b_id = me_resp.json()["user_id"]

    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Test invalid login
    bad_login = client.post("/api/auth/login", json={"email": "user_a@example.com", "password": "wrongpassword"})
    assert bad_login.status_code == 401

    # 4. Get /auth/me for User A
    me_resp = client.get("/api/auth/me", headers=headers_a)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "user_a"

    # 5. User A follows User B
    follow_resp = client.post(f"/api/users/{user_b_id}/follow", headers=headers_a)
    if follow_resp.status_code == 409:
        # Already following, unfollow first
        client.delete(f"/api/users/{user_b_id}/follow", headers=headers_a)
        follow_resp = client.post(f"/api/users/{user_b_id}/follow", headers=headers_a)
    
    assert follow_resp.status_code == 201
    assert follow_resp.json()["follower_id"] == user_a_id
    assert follow_resp.json()["followed_id"] == user_b_id

    # 6. Check User B profile (followers count should be updated)
    profile_b = client.get(f"/api/users/{user_b_id}", headers=headers_a)
    assert profile_b.status_code == 200
    assert profile_b.json()["followers_count"] >= 1

    # 7. User A unfollows User B
    unfollow_resp = client.delete(f"/api/users/{user_b_id}/follow", headers=headers_a)
    assert unfollow_resp.status_code == 200

    # 8. User A creates a post
    post_resp = client.post("/api/posts/", json={"body": "Hello from User A"}, headers=headers_a)
    assert post_resp.status_code == 201

    # 9. Get all users with auth
    users_resp = client.get("/api/users/", headers=headers_a)
    assert users_resp.status_code == 200
    assert len(users_resp.json()) >= 2

    # 10. Access protected route without token (should fail 401)
    no_auth = client.get("/api/users/")
    assert no_auth.status_code == 401

    # 11. Access protected route with bad token (should fail 401)
    bad_token = client.get("/api/users/", headers={"Authorization": "Bearer invalidtoken123"})
    assert bad_token.status_code == 401
