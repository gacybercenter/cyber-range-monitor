from fastapi.testclient import TestClient


class TestUserRoutes:
    """Integration tests for user routes."""

    def test_get_current_user_success(self, test_admin_client: TestClient) -> None:
        """Test successful retrieval of current user."""

        response = test_admin_client.get("/users/me/")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "id" in data

    def test_get_current_user_unauthorized(self, test_client: TestClient) -> None:
        """Test retrieval of current user without authentication."""
        response = test_client.get("/users/me/")
        assert response.status_code in (401, 403)

    def test_get_all_users_as_admin(self, test_admin_client: TestClient) -> None:
        """Test getting all users as admin."""

        response = test_admin_client.get("/users/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(
            data["data"]) >= 3, 'either the seed changed or the endpoint is broken.'

        usernames = [user["username"] for user in data["data"]]
        assert "admin" in usernames
        assert "user" in usernames
        assert "guest" in usernames

    def test_get_all_users_as_user(self, test_user_client: TestClient) -> None:
        """Test getting all users as regular user (should only see user and guest)."""

        response = test_user_client.get("/users/")

        assert response.status_code == 200
        data = response.json()

        usernames = [user["username"] for user in data["data"]]
        assert "admin" not in usernames
        assert "user" in usernames
        assert "guest" in usernames

    def test_get_all_as_guest(self, test_guest_client: TestClient) -> None:
        """Test getting all users as guest (should only see guest)."""

        response = test_guest_client.get("/users/")

        assert response.status_code == 200
        data = response.json()

        usernames = [user["username"] for user in data["data"]]
        assert "admin" not in usernames
        assert "user" not in usernames
        assert "guest" in usernames

    def test_get_all_details_as_admin(self, test_admin_client: TestClient) -> None:
        """Test getting detailed user info as admin."""
        response = test_admin_client.get("/users/details")

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


    def test_get_user_details_by_invalid_id(self, test_admin_client: TestClient) -> None:
        """Test getting details of a non-existent user."""

        response = test_admin_client.get("/users/details/6969/")

        assert response.status_code == 404

    def test_create_user_admin(self, test_admin_client: TestClient) -> None:
        """Test creating a new user as admin."""

        form_data = {
            "username": "newUser",
            "password": "password123",
            "role": "user"
        }

        response = test_admin_client.post(
            "/users/",
            data=form_data
        )

        assert response.status_code == 201
        user_data = response.json()
        assert user_data["username"] == "newUser"
        assert user_data["role"] == "user"

    def test_create_user_duplicate_username(self, test_admin_client: TestClient) -> None:
        """Test creating a user with a username that already exists."""

        form_data = {
            "username": "admin",  # existing user
            "password": "password123",
            "role": "user"
        }

        response = test_admin_client.post(
            "/users/",
            data=form_data
        )
        assert response.status_code == 400

    def test_create_user_as_other(self, test_admin_client: TestClient) -> None:
        """Test creating a user as non-admin (should fail)."""

        form_data = {
            "username": "new_user2",
            "password": "password123",
            "role": "user"
        }

        response = test_admin_client.post(
            "/users/",
            data=form_data
        )

        assert response.status_code in (401, 403)

    def test_update_user_as_admin(self, test_admin_client: TestClient) -> None:
        """Test updating a user as admin."""

        form_data = {
            "username": "update_tests",
            "password": "oldpassword",
            "role": "user"
        }

        create_response = test_admin_client.post("/users/", data=form_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        update_data = {
            "username": "updated_name",
            "password": "newpassword",
            "role": "read_only"
        }

        update_response = test_admin_client.patch(
            f"/users/{user_id}/",
            data=update_data
        )

        assert update_response.status_code == 202
        updated_user = update_response.json()
        assert updated_user["username"] == "updated_name"
        assert updated_user["role"] == "read_only"

    def test_update_user_taken_username(self, test_admin_client: TestClient) -> None:
        """Test updating a user to a username that's already taken."""

        form_data = {
            "username": "uniquest_name",
            "password": "password",
            "role": "user"
        }

        create_response = test_admin_client.post("/users/", data=form_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        update_data = {
            "username": "admin"
        }

        update_response = test_admin_client.patch(
            f"/users/{user_id}/",
            data=update_data
        )

        assert update_response.status_code == 400

    def test_update_nonexistent_user(self, test_admin_client: TestClient) -> None:
        """Test updating a user that doesn't exist."""
        update_data = {
            "username": "lol"
        }

        response = test_admin_client.patch(
            "/users/6969/",
            data=update_data
        )

        assert response.status_code == 404

    def test_delete_user_admin(self, test_admin_client: TestClient) -> None:
        """Test deleting a user as admin."""

        form_data = {
            "username": "pls_delete_me",
            "password": "password",
            "role": "user"
        }

        create_response = test_admin_client.post("/users/", data=form_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        delete_response = test_admin_client.delete(f"/users/{user_id}/")

        assert delete_response.status_code == 200

        check_response = test_admin_client.get(f"/users/{user_id}/")
        assert check_response.status_code == 404

    def test_admin_delete_self(self, test_admin_client: TestClient) -> None:
        """Test an admin trying to delete themselves (should fail)."""

        response = test_admin_client.get("/users/me/")
        admin_id = response.json()["id"]

        delete_response = test_admin_client.delete(f"/users/{admin_id}/")

        assert delete_response.status_code == 403


    def test_read_user_same_role(self, test_user_client: TestClient) -> None:
        """Test reading a user of the same role."""

        me_response = test_user_client.get("/users/me/")
        my_id = me_response.json()["id"]

        response = test_user_client.get(f"/users/{my_id}/")

        assert response.status_code == 200
        assert response.json()["username"] == "user"

    def test_read_user_lower_role(self, test_user_client: TestClient) -> None:
        """Test reading a user of lower role."""

        all_response = test_user_client.get("/users/")
        users = all_response.json()["data"]
        guest_id = next(user["id"]
                        for user in users if user["username"] == "guest")

        response = test_user_client.get(f"/users/{guest_id}/")

        assert response.status_code == 200
        assert response.json()["username"] == "guest"