import pytest
import json

from fastapi.testclient import TestClient

from typing import Dict, Any

from app.users.model import Role
from app.auth.const import AUTH_COOKIE_NAME


class TestUserRoutes:
    """Integration tests for user routes."""

    def test_get_current_user_success(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test successful retrieval of current user."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/me/")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "id" in data

    def test_get_current_user_unauthorized(self, test_client: TestClient) -> None:
        """Test retrieval of current user without authentication."""
        test_client.cookies.clear()
        response = test_client.get("/users/me/")
        assert response.status_code in (401, 403)

    def test_get_all_users_as_admin(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test getting all users as admin."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(
            data["data"]) >= 3, 'either the seed changed or the endpoint is broken.'

        usernames = [user["username"] for user in data["data"]]
        assert "admin" in usernames
        assert "user" in usernames
        assert "guest" in usernames

    def test_get_all_users_as_user(self, test_client: TestClient, test_user_key: str) -> None:
        """Test getting all users as regular user (should only see user and guest)."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)

        response = test_client.get("/users/")

        assert response.status_code == 200
        data = response.json()

        usernames = [user["username"] for user in data["data"]]
        assert "admin" not in usernames
        assert "user" in usernames
        assert "guest" in usernames

    def test_get_all_as_guest(self, test_client: TestClient, test_guest_key: str) -> None:
        """Test getting all users as guest (should only see guest)."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_guest_key)

        response = test_client.get("/users/")

        assert response.status_code == 200
        data = response.json()

        usernames = [user["username"] for user in data["data"]]
        assert "admin" not in usernames
        assert "user" not in usernames
        assert "guest" in usernames

    def test_get_all_details_as_admin(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test getting detailed user info as admin."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/details")

        assert response.status_code == 200
        data = response.json()

        assert len(
            data["data"]) >= 3, 'either the seed changed or the endpoint is broken.'

        user = data["data"][0]
        assert "createdAt" in user, 'either the schema changed or the endpoint is broken'
        assert "updatedAt" in user, 'either the schema changed or the endpoint is broken'
        assert "username" in user, 'either the schema changed or the endpoint is broken'
        assert "role" in user, 'either the schema changed or the endpoint is broken'
        assert "id" in user, 'either the schema changed or the endpoint is broken'

    def test_get_all_details_as_other(self, test_client: TestClient, test_user_key: str) -> None:
        """Test getting detailed user info as non-admin (should fail)."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)

        response = test_client.get("/users/details")

        assert response.status_code in (401, 403)

    def test_get_details_by_id_admin(self, test_client: TestClient, test_admin_key):
        """Test getting a specific user's details as admin."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/")
        users = response.json()["data"]
        user_id = next(user["id"]
                       for user in users if user["username"] == "user")

        response = test_client.get(f"/users/details/{user_id}/")

        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "user"
        assert "createdAt" in user_data
        assert "updatedAt" in user_data

    def test_get_user_details_by_invalid_id(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test getting details of a non-existent user."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/details/6969/")

        assert response.status_code == 404

    def test_create_user_admin(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test creating a new user as admin."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        form_data = {
            "username": "newUser",
            "password": "password123",
            "role": "user"
        }

        response = test_client.post(
            "/users/",
            data=form_data
        )

        assert response.status_code == 201
        user_data = response.json()
        assert user_data["username"] == "newUser"
        assert user_data["role"] == "user"

    def test_create_user_duplicate_username(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test creating a user with a username that already exists."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        form_data = {
            "username": "admin",  # existing user
            "password": "password123",
            "role": "user"
        }

        response = test_client.post(
            "/users/",
            data=form_data
        )
        assert response.status_code == 400

    def test_create_user_as_other(self, test_client: TestClient, test_user_key: str) -> None:
        """Test creating a user as non-admin (should fail)."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)

        form_data = {
            "username": "new_user2",
            "password": "password123",
            "role": "user"
        }

        response = test_client.post(
            "/users/",
            data=form_data
        )

        assert response.status_code in (401, 403)

    def test_update_user_as_admin(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test updating a user as admin."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        form_data = {
            "username": "update_tests",
            "password": "oldpassword",
            "role": "user"
        }

        create_response = test_client.post("/users/", data=form_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        update_data = {
            "username": "updated_name",
            "password": "newpassword",
            "role": "read_only"
        }

        update_response = test_client.patch(
            f"/users/{user_id}/",
            data=update_data
        )

        assert update_response.status_code == 202
        updated_user = update_response.json()
        assert updated_user["username"] == "updated_name"
        assert updated_user["role"] == "read_only"

    def test_update_user_taken_username(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test updating a user to a username that's already taken."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        form_data = {
            "username": "uniquest_name",
            "password": "password",
            "role": "user"
        }

        create_response = test_client.post("/users/", data=form_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        update_data = {
            "username": "admin"
        }

        update_response = test_client.patch(
            f"/users/{user_id}/",
            data=update_data
        )

        assert update_response.status_code == 400

    def test_update_nonexistent_user(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test updating a user that doesn't exist."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
        update_data = {
            "username": "doesnt_matter"
        }

        response = test_client.patch(
            "/users/6969/",
            data=update_data
        )

        assert response.status_code == 404

    def test_delete_user_admin(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test deleting a user as admin."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        form_data = {
            "username": "pls_delete_me",
            "password": "password",
            "role": "user"
        }

        create_response = test_client.post("/users/", data=form_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        delete_response = test_client.delete(f"/users/{user_id}/")

        assert delete_response.status_code == 200

        check_response = test_client.get(f"/users/{user_id}/")
        assert check_response.status_code == 404

    def test_admin_delete_self(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test an admin trying to delete themselves (should fail)."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/me/")
        admin_id = response.json()["id"]

        delete_response = test_client.delete(f"/users/{admin_id}/")

        assert delete_response.status_code == 403

    def test_delete_nonexistent_user(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test deleting a user that doesn't exist."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.delete("/users/6969/")

        assert response.status_code == 404

    def test_read_user_same_role(self, test_client: TestClient, test_user_key: str) -> None:
        """Test reading a user of the same role."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)

        me_response = test_client.get("/users/me/")
        my_id = me_response.json()["id"]

        response = test_client.get(f"/users/{my_id}/")

        assert response.status_code == 200
        assert response.json()["username"] == "user"

    async def test_read_user_lower_role(self, test_client: TestClient, test_user_key: str) -> None:
        """Test reading a user of lower role."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)

        all_response = test_client.get("/users/")
        users = all_response.json()["data"]
        guest_id = next(user["id"] for user in users if user["username"] == "guest")

        response = test_client.get(f"/users/{guest_id}/")

        assert response.status_code == 200
        assert response.json()["username"] == "guest"

    def test_read_user_higher_role(
        self,
        test_client: TestClient,
        test_user_key: str,
        test_admin_key: str
    ) -> None:
        """Test reading a user of higher role (should fail)."""

        admin_response = test_client.get(
            "/users/me/", cookies={AUTH_COOKIE_NAME: test_admin_key})
        admin_id = admin_response.json()["id"]

        test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)
        response = test_client.get(f"/users/{admin_id}/")

        assert response.status_code == 403

    def test_read_nonexistent_user(self, test_client: TestClient, test_admin_key: str) -> None:
        """Test reading a user that doesn't exist."""
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)

        response = test_client.get("/users/6969/")

        assert response.status_code == 404
