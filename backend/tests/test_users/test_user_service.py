import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.service import (
    UserService, AuthForm, CreateUserForm, User, UpdateUserForm
)


@pytest_asyncio.fixture
async def test_user_service(test_db: AsyncSession) -> UserService:
    return UserService(test_db)


@pytest_asyncio.fixture
async def test_user_model(test_user_service: UserService) -> User:
    user = await test_user_service.get_username('admin')
    assert user is not None, 'Admin user does not exist'
    return user


@pytest_asyncio.fixture
async def test_guest_model(test_user_service: UserService) -> User:
    user = await test_user_service.get_username('guest')
    assert user is not None, 'Guest user does not exist'
    return user


@pytest_asyncio.fixture
async def test_admin_model(test_user_service: UserService) -> User:
    user = await test_user_service.get_username('admin')
    assert user is not None, 'Admin user does not exist'
    return user


@pytest.mark.asyncio
async def test_authentication(test_user_service: UserService) -> None:
    good_auth_form = AuthForm(username='admin', password='admin')
    user = await test_user_service.authenticate(good_auth_form)
    assert user is not None, 'Valid credentials did not work'

    bad_user = AuthForm(
        username='admin',
        password='wrong_password'
    )
    assert await test_user_service.authenticate(bad_user) is None, 'Invalid credentials worked'

    unknown_username = AuthForm(
        username='unknown',
        password='admin'
    )
    assert await test_user_service.authenticate(unknown_username) is None, 'Bad username worked'


@pytest.mark.asyncio
async def test_user_create(test_user_service: UserService) -> None:
    test_user_form = CreateUserForm(
        username='test',
        password='test',
        role='admin'  # type: ignore
    )
    model = test_user_form.model_dump()
    test_user_service.hash_password_in_req(model)

    assert 'password' not in model, 'Password was not removed from the request'
    assert 'password_hash' in model, 'Password hash was not added to the request'
    assert model['password_hash'] != 'test', 'Password hash was not hashed'

    user_orm = await test_user_service.create_user(test_user_form)
    assert user_orm is not None, 'User was not created'


@pytest.mark.asyncio
async def test_duplicate_username(test_user_service: UserService) -> None:
    with pytest.raises(Exception):
        duplicate_user_form = CreateUserForm(
            username='admin',
            password='admin',
            role='admin'  # type: ignore
        )
        await test_user_service.create_user(duplicate_user_form)


@pytest.mark.asyncio
async def test_admin_deletes_self(test_user_service: UserService) -> None:
    admin = await test_user_service.get_username('admin')
    assert admin is not None, 'Admin user does not exist'
    with pytest.raises(Exception):
        await test_user_service.delete_user(admin.id, admin.username)
    assert await test_user_service.get_username('admin') is not None, 'Admin user was deleted'


@pytest.mark.asyncio
async def test_delete_user(test_user_service: UserService) -> None:
    guest = await test_user_service.get_username('guest')
    assert guest is not None, 'Guest user does not exist'
    await test_user_service.delete_user(guest.id, 'admin')

    assert await test_user_service.get_username('guest') is None, 'Guest user was not deleted'


@pytest.mark.asyncio
async def test_role_based_read(
    test_guest_model: User,
    test_user_model: User,
    test_admin_model: User,
    test_user_service: UserService
) -> None:
    for i, user in enumerate([test_guest_model, test_user_model, test_admin_model]):
        items = await test_user_service.role_based_read_all(user)
        assert items and len(
            items) == i + 1, f'User {user.username} should see {i + 1} user(s)'


@pytest.mark.asyncio
async def test_update_user(
    test_guest_model: User,
    test_user_service: UserService
) -> None:

    update_form = UpdateUserForm(
        username='admin',
        password='admin',
        role='read_only'  # type: ignore
    )
    # Username is taken
    with pytest.raises(Exception):
        await test_user_service.update_user(test_guest_model.id, update_form)
    update_form = UpdateUserForm(
        username='guest_2',
        password='guest_2',
        role='read_only'  # type: ignore
    )
    await test_user_service.update_user(test_guest_model.id, update_form)
    assert await test_user_service.get_username('guest_2') is not None, 'User was not updated'
