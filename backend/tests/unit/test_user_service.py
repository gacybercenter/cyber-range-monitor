from typing import Any
import pytest
import pytest_asyncio

from app.extensions.security import crypto
from app.core.errors import HTTPBadRequest
from app.users.service import UserService
from app.users.errors import DeleteSelfForbidden, UserNotFound
from app.users.schema import AuthForm, CreateUserForm, UpdateUserForm
from app.users.model import Role


@pytest.mark.asyncio
class TestUserService:
    """Tests for the UserService class."""

    @pytest_asyncio.fixture
    async def user_service(self, test_db) -> UserService:
        """Create a UserService instance with the test database session."""
        return UserService(test_db)

    async def test_authenticate_flow(self, user_service: UserService, mock_auth_form) -> None:
        """Test successful authentication with valid credentials."""
        authenticated_user = await user_service.authenticate(mock_auth_form)

        assert authenticated_user is not None
        assert authenticated_user.username == "user"
        assert authenticated_user.role == Role.USER

        invalid_auth = AuthForm(username="user", password="wrong_password")

        authenticated_user = await user_service.authenticate(invalid_auth)
        assert authenticated_user is None

    async def test_authenticate_nonexistent_user(self, user_service: UserService) -> Any:
        """Test authentication with a username that doesn't exist."""
        invalid_auth = AuthForm(username="nonexistent", password="password")

        authenticated_user = await user_service.authenticate(invalid_auth)
        assert authenticated_user is None

    async def test_get_username_existing(self, user_service: UserService) -> None:
        """Test retrieving an existing user by username."""
        user = await user_service.get_username("admin")

        assert user is not None
        assert user.username == "admin"
        assert user.role == Role.ADMIN

    async def test_get_username_nonexistent(self, user_service: UserService) -> None:
        """Test retrieving a non-existent user by username."""
        user = await user_service.get_username("nonexistent")
        assert user is None

    async def test_require_username_existing(self, user_service: UserService) -> None:
        """Test requiring an existing username."""
        user = await user_service.require_username("guest")

        assert user is not None
        assert user.username == "guest"
        assert user.role == Role.READ_ONLY

    async def test_require_username_nonexistent(self, user_service: UserService) -> None:
        """Test requiring a non-existent username throws an error."""
        with pytest.raises(UserNotFound):
            await user_service.require_username("nonexistent")

    async def test_create_user(self, user_service: UserService) -> None:
        """Test creating a new user."""
        create_form = CreateUserForm(
            username="new_user",
            password="password123",
            role=Role.USER
        )

        new_user = await user_service.create_user(create_form)

        assert new_user is not None
        assert new_user.username == "new_user"
        assert new_user.role == Role.USER

        assert new_user.password_hash != "password123"
        assert crypto.check_password("password123", new_user.password_hash)

        retrieved_user = await user_service.get_username("new_user")
        assert retrieved_user is not None
        assert retrieved_user.id == new_user.id

    async def test_hash_password_in_req(self, user_service: UserService) -> None:
        """Test the hash_password_in_req method."""
        req = {
            "username": "test_user",
            "password": "testpassword",
            "role": Role.USER
        }

        user_service.hash_password_in_req(req)

        assert "password" not in req
        assert "password_hash" in req
        assert crypto.check_password("testpassword", req["password_hash"])

    async def test_update_user_success(self, user_service: UserService) -> None:
        """Test successfully updating a user."""
        create_form = CreateUserForm(
            username="update_mes",
            password="oldpassword",
            role=Role.USER
        )
        user = await user_service.create_user(create_form)

        update_form = UpdateUserForm(
            username="updated_names",
            password="newpassword",
            role=Role.READ_ONLY
        )

        updated_user = await user_service.update_user(user.id, update_form)

        assert updated_user.username == "updated_names"
        assert updated_user.role == Role.READ_ONLY
        assert crypto.check_password("newpassword", updated_user.password_hash)

        retrieved_user = await user_service.get_username("updated_names")
        assert retrieved_user is not None
        assert retrieved_user.id == user.id

    async def test_update_user_nonexistent(self, user_service: UserService) -> None:
        """Test updating a non-existent user throws an error."""
        update_form = UpdateUserForm(username="newname")

        with pytest.raises(UserNotFound):
            await user_service.update_user(9999, update_form)

    async def test_update_user_taken_username(self, user_service: UserService, test_db):
        """Test updating to a username that's already taken throws an error."""
        create_form = CreateUserForm(
            username="unique_name",
            password="password",
            role=Role.USER
        )
        user = await user_service.create_user(create_form)

        update_form = UpdateUserForm(username="admin")

        with pytest.raises(HTTPBadRequest, match="Username is already taken"):
            await user_service.update_user(user.id, update_form)

    async def test_update_user_empty_data(self, user_service: UserService, test_db) -> None:
        """Test updating with empty data throws an error."""
        create_form = CreateUserForm(
            username="empty_update",
            password="password",
            role=Role.USER
        )
        user = await user_service.create_user(create_form)

        update_form = UpdateUserForm()

        with pytest.raises(HTTPBadRequest, match="Cannot update a user with empty data"):
            await user_service.update_user(user.id, update_form)

    async def test_delete_user_success(self, user_service: UserService, test_db):
        """Test successfully deleting a user."""
        create_form = CreateUserForm(
            username="deleteme",
            password="password",
            role=Role.USER
        )
        user = await user_service.create_user(create_form)

        await user_service.delete_user(user.id, "admin")

        deleted_user = await user_service.get_by_id(user.id)
        assert deleted_user is None

    async def test_delete_user_nonexistent(self, user_service: UserService) -> None:
        """Test deleting a non-existent user throws an error."""
        with pytest.raises(UserNotFound):
            await user_service.delete_user(9999, "admin")

    async def test_delete_self_forbidden(self, user_service: UserService, test_db) -> None:
        """Test an admin cannot delete themselves."""
        admin = await user_service.get_username("admin")
        assert admin is not None
        with pytest.raises(DeleteSelfForbidden):
            await user_service.delete_user(admin.id, "admin")

    async def test_delete_nonexistent_admin(self, user_service: UserService, test_db) -> None:
        """Test deletion by a non-existent admin throws an error."""
        create_form = CreateUserForm(
            username="another_user",
            password="password",
            role=Role.USER
        )
        user = await user_service.create_user(create_form)

        with pytest.raises(DeleteSelfForbidden):
            await user_service.delete_user(user.id, "nonexistent_admin")

    async def test_role_based_read_all_admin(self, user_service: UserService) -> None:
        """Test an admin can see all users."""
        admin = await user_service.get_username("admin")
        assert admin is not None
        users = await user_service.role_based_read_all(admin) 

        assert users is not None
        
        assert len(users) >= 3

        usernames = [u.username for u in users]
        assert "admin" in usernames
        assert "user" in usernames
        assert "guest" in usernames

    async def test_role_based_read_all_user(self, user_service) -> Any:
        """Test a regular user can see users with equal or lower role level."""
        regular_user = await user_service.get_username("user")

        users = await user_service.role_based_read_all(regular_user)

        assert "admin" not in [u.username for u in users]
        assert "user" in [u.username for u in users]
        assert "guest" in [u.username for u in users]

    async def test_role_based_read_all_guest(self, user_service) -> Any:
        """Test a guest can only see guest users."""
        guest = await user_service.get_username("guest")

        users = await user_service.role_based_read_all(guest)

        assert "admin" not in [u.username for u in users]
        assert "user" not in [u.username for u in users]
        assert "guest" in [u.username for u in users]

    async def test_read_all(self, user_service) -> Any:
        """Test reading all users."""
        users = await user_service.read_all()

        assert len(users) >= 3

        usernames = [u.username for u in users]
        assert "admin" in usernames
        assert "user" in usernames
        assert "guest" in usernames
