import pytest
from fastapi.testclient import TestClient

from .const import BAD_DATA, MISSING_CONTENT, NOT_PRESENT, UNEXPECTED_STATUS


@pytest.mark.integration
class TestUserRoutes:
    """Integration tests for user routes."""

    def test_get_current_user_success(self, test_admin_client: TestClient) -> None:
        """Test successful retrieval of current user."""

        response = test_admin_client.get('/users/me/')

        assert response.status_code == 200, UNEXPECTED_STATUS
        data = response.json()
        assert data['username'] == 'admin', BAD_DATA
        assert data['role'] == 'admin', BAD_DATA
        assert 'id' in data, MISSING_CONTENT

    def test_get_current_user_unauthorized(self, test_client: TestClient) -> None:
        """Test retrieval of current user without authentication."""
        response = test_client.get('/users/me/')
        assert response.status_code in (401, 403), UNEXPECTED_STATUS

    def test_get_all_users_as_admin(self, test_admin_client: TestClient) -> None:
        """Test getting all users as admin."""

        response = test_admin_client.get('/users/')

        assert response.status_code == 200, UNEXPECTED_STATUS
        data = response.json()
        assert 'data' in data, MISSING_CONTENT
        assert len(data['data']) >= 3, (
            'either the seed changed or the endpoint is broken.'
        )

        usernames = [user['username'] for user in data['data']]
        assert 'admin' in usernames, MISSING_CONTENT
        assert 'user' in usernames, MISSING_CONTENT
        assert 'guest' in usernames, MISSING_CONTENT

    def test_get_all_users_as_user(self, test_user_client: TestClient) -> None:
        """Test getting all users as regular user (should only see user and guest)."""

        response = test_user_client.get('/users/')

        assert response.status_code == 200, UNEXPECTED_STATUS
        data = response.json()

        usernames = [user['username'] for user in data['data']]
        assert 'admin' not in usernames, MISSING_CONTENT
        assert 'user' in usernames, MISSING_CONTENT
        assert 'guest' in usernames, MISSING_CONTENT

    def test_get_all_as_guest(self, test_guest_client: TestClient) -> None:
        """Test getting all users as guest (should only see guest)."""

        response = test_guest_client.get('/users/')

        assert response.status_code == 200, UNEXPECTED_STATUS
        data = response.json()

        usernames = [user['username'] for user in data['data']]
        assert 'admin' not in usernames, NOT_PRESENT
        assert 'user' not in usernames, NOT_PRESENT
        assert 'guest' in usernames, NOT_PRESENT

    def test_get_all_details_as_admin(self, test_admin_client: TestClient) -> None:
        """Test getting detailed user info as admin."""
        response = test_admin_client.get('/users/details')

        assert response.status_code == 200, UNEXPECTED_STATUS
        data = response.json()
        err = 'either the schema changed or the endpoint is broken'

        assert len(data['data']) >= 3, err

        user = data['data'][0]
        assert 'createdAt' in user, err
        assert 'updatedAt' in user, err
        assert 'username' in user, err
        assert 'role' in user, err
        assert 'id' in user, err

    def test_get_user_details_by_invalid_id(
        self, test_admin_client: TestClient
    ) -> None:
        """Test getting details of a non-existent user."""

        response = test_admin_client.get('/users/details/6969/')

        assert response.status_code == 404, UNEXPECTED_STATUS

    def test_create_user_admin(self, test_admin_client: TestClient) -> None:
        """Test creating a new user as admin."""

        body = {'username': 'newUser', 'password': 'password123', 'role': 'user'}

        response = test_admin_client.post('/users/', json=body)

        assert response.status_code == 201, UNEXPECTED_STATUS
        user_data = response.json()
        assert user_data['username'] == 'newUser', BAD_DATA
        assert user_data['role'] == 'user', BAD_DATA

    def test_create_user_duplicate_username(
        self, test_admin_client: TestClient
    ) -> None:
        """Test creating a user with a username that already exists."""

        body = {
            'username': 'admin',  # existing user
            'password': 'password123',
            'role': 'user',
        }

        response = test_admin_client.post('/users/', json=body)
        assert response.status_code == 400, UNEXPECTED_STATUS

    def test_create_user_as_other(self, test_user_client: TestClient) -> None:
        """Test creating a user as non-admin (should fail)."""

        body = {'username': 'new_user2', 'password': 'password123', 'role': 'user'}

        response = test_user_client.post('/users/', json=body)

        assert response.status_code in (401, 403), UNEXPECTED_STATUS

    def test_update_user_as_admin(self, test_admin_client: TestClient) -> None:
        """Test updating a user as admin."""

        body = {'username': 'update_tests', 'password': 'oldpassword', 'role': 'user'}

        create_response = test_admin_client.post('/users/', json=body)
        assert create_response.status_code == 201, UNEXPECTED_STATUS
        user_id = create_response.json()['id']

        update_data = {
            'username': 'updated_name',
            'password': 'newpassword',
            'role': 'read_only',
        }

        update_response = test_admin_client.patch(
            f'/users/{user_id}/', json=update_data
        )

        assert update_response.status_code == 202, UNEXPECTED_STATUS
        updated_user = update_response.json()
        assert updated_user['username'] == 'updated_name', BAD_DATA
        assert updated_user['role'] == 'read_only', BAD_DATA

    def test_update_user_taken_username(self, test_admin_client: TestClient) -> None:
        """Test updating a user to a username that's already taken."""

        body = {'username': 'uniquest_name', 'password': 'password', 'role': 'user'}

        create_response = test_admin_client.post('/users/', json=body)
        assert create_response.status_code == 201, UNEXPECTED_STATUS
        user_id = create_response.json()['id']

        update_data = {'username': 'admin'}

        update_response = test_admin_client.patch(
            f'/users/{user_id}/', json=update_data
        )

        assert update_response.status_code == 400, UNEXPECTED_STATUS

    def test_update_nonexistent_user(self, test_admin_client: TestClient) -> None:
        """Test updating a user that doesn't exist."""
        update_data = {'username': 'lol'}

        response = test_admin_client.patch('/users/6969/', json=update_data)

        assert response.status_code == 404, UNEXPECTED_STATUS

    def test_delete_user_admin(self, test_admin_client: TestClient) -> None:
        """Test deleting a user as admin."""

        body = {'username': 'pls_delete_me', 'password': 'password', 'role': 'user'}

        create_response = test_admin_client.post('/users/', json=body)
        assert create_response.status_code == 201, UNEXPECTED_STATUS
        user_id = create_response.json()['id']

        delete_response = test_admin_client.delete(f'/users/{user_id}/')

        assert delete_response.status_code == 200, UNEXPECTED_STATUS

        check_response = test_admin_client.get(f'/users/{user_id}/')
        assert check_response.status_code == 404, UNEXPECTED_STATUS

    def test_admin_delete_self(self, test_admin_client: TestClient) -> None:
        """Test an admin trying to delete themselves (should fail)."""

        response = test_admin_client.get('/users/me/')
        admin_id = response.json()['id']

        delete_response = test_admin_client.delete(f'/users/{admin_id}/')

        assert delete_response.status_code == 403, UNEXPECTED_STATUS

    def test_read_user_same_role(self, test_user_client: TestClient) -> None:
        """Test reading a user of the same role."""

        me_response = test_user_client.get('/users/me/')
        my_id = me_response.json()['id']

        response = test_user_client.get(f'/users/{my_id}/')

        assert response.status_code == 200, UNEXPECTED_STATUS
        assert response.json()['username'] == 'user'

    def test_read_user_lower_role(self, test_user_client: TestClient) -> None:
        """Test reading a user of lower role."""

        all_response = test_user_client.get('/users/')
        users = all_response.json()['data']
        guest_id = next(user['id'] for user in users if user['username'] == 'guest')

        response = test_user_client.get(f'/users/{guest_id}/')

        assert response.status_code == 200, UNEXPECTED_STATUS
        assert response.json()['username'] == 'guest', BAD_DATA

    def test_auth_as_deleted_user(self, test_client: TestClient) -> None:
        """Test authentication with a deleted user."""

        body = {'username': 'jjj', 'password': 'jjj', 'role': 'admin'}

        create_response = test_client.post('/users/', json=body)
        assert create_response.status_code == 201, UNEXPECTED_STATUS

        user_id = create_response.json()['id']

        login = test_client.post('/auth/login', json=body)
        assert login.status_code == 200, UNEXPECTED_STATUS
        key = login.json().get('apiKey')
        assert key, MISSING_CONTENT

        delete_response = test_client.delete(f'/users/{user_id}/')
        assert delete_response.status_code == 200, UNEXPECTED_STATUS

        protected_res = test_client.get('/users/me/')
        assert protected_res.status_code != 200, UNEXPECTED_STATUS
