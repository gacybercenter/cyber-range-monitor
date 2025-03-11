import pytest

from app.auth.const import AUTH_COOKIE_NAME


@pytest.mark.asyncio
async def test_full_auth_flow(test_client) -> None:
    """Test the complete authentication flow from login to logout."""
    login_response = test_client.post(
        "/auth/login/",
        data={"username": "admin", "password": "admin"}
    )

    assert login_response.status_code == 200
    assert login_response.json() == {"message": "Login successful"}

    assert AUTH_COOKIE_NAME in login_response.cookies
    api_key_cookie = login_response.cookies[AUTH_COOKIE_NAME]
    assert api_key_cookie

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key_cookie)
    protected_response = test_client.get("/users/")

    assert protected_response.status_code == 200

    logout_response = test_client.post("/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logout successful"}

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key_cookie)
    invalid_response = test_client.get("/users/")

    assert invalid_response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(test_client) -> None:
    """Test login with invalid credentials."""
    response = test_client.post(
        "/auth/login/",
        data={"username": "nonexistent", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert AUTH_COOKIE_NAME not in response.cookies


@pytest.mark.asyncio
async def test_session_hijacking_detection(test_client) -> None:
    """Test that changing the client identity causes session invalidation."""
    login_response = test_client.post(
        "/auth/login/",
        data={"username": "admin", "password": "admin"}
    )

    assert login_response.status_code == 200
    api_key_cookie = login_response.cookies[AUTH_COOKIE_NAME]

    original_headers = test_client.headers.copy()

    test_client.headers["user-agent"] = "Different Browser/1.0"
    test_client.cookies.set(AUTH_COOKIE_NAME, api_key_cookie)

    hijack_response = test_client.get("/users/")

    assert hijack_response.status_code == 401

    test_client.headers = original_headers


@pytest.mark.asyncio
async def test_concurrent_sessions(test_client) -> None:
    """Test that a user can have multiple concurrent sessions."""
    login_response1 = test_client.post(
        "/auth/login/",
        data={"username": "admin", "password": "admin"}
    )
    assert login_response1.status_code == 200
    api_key1 = login_response1.cookies[AUTH_COOKIE_NAME]

    login_response2 = test_client.post(
        "/auth/login/",
        data={"username": "admin", "password": "admin"}
    )
    assert login_response2.status_code == 200
    api_key2 = login_response2.cookies[AUTH_COOKIE_NAME]

    assert api_key1 != api_key2

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key1)
    response1 = test_client.get("/users/")
    assert response1.status_code == 200

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key2)
    response2 = test_client.get("/users/")
    assert response2.status_code == 200

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key1)
    logout_response = test_client.post("/auth/logout")
    assert logout_response.status_code == 200

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key1)
    invalid_response = test_client.get("/users/")
    assert invalid_response.status_code == 401

    test_client.cookies.set(AUTH_COOKIE_NAME, api_key2)
    valid_response = test_client.get("/users/")
    assert valid_response.status_code == 200


@pytest.mark.asyncio
async def test_logout_without_session(test_client) -> None:
    """Test logout endpoint behavior when no session exists."""
    test_client.cookies.clear()

    response = test_client.post("/auth/logout/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_deleted_user(test_client, test_admin_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    new_user_res = test_client.post('/users/', data={
        'username': 'test_user',
        'password': 'test_password',
        'role': 'user'
    })
    assert new_user_res.status_code == 201, 'Failed to create test user'

    new_uid = new_user_res.json()['id']

    new_user_login = test_client.post(
        "/auth/login/",
        data={"username": 'test_user', "password": 'test_password'}
    )
    assert new_user_login.status_code == 200, 'Failed to login test user'
    new_user_key = new_user_login.cookies[AUTH_COOKIE_NAME]

    delete_user_res = test_client.delete(f'/users/{new_uid}/')

    assert delete_user_res.status_code == 200, 'Failed to delete test user'

    test_client.cookies.set(AUTH_COOKIE_NAME, new_user_key)

    me_res = test_client.get('/users/me/')
    assert me_res.status_code in (
        401, 403
    ), 'Deleted user could still access their profile'
