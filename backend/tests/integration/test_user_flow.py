import pytest

from app.auth.const import AUTH_COOKIE_NAME
from app.users.model import Role, User


def test_create_user(test_client, test_admin_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    new_user = {
        'username': 'test_user',
        'password': 'test_password',
        'role': 'user'
    }
    new_user_res = test_client.post('/users/', data=new_user)
    assert new_user_res.status_code == 201, 'Failed to create test user'

    bad_username_res = test_client.post('/users/', data=new_user)
    assert bad_username_res.status_code == 400, 'Failed to create test user with duplicate username'

    new_user['username'] = 'test_user2'
    new_user['role'] = 'bad-role'

    bad_role_res = test_client.post('/users/', data=new_user)
    assert bad_role_res.status_code == 400, 'Failed to create test user with invalid role'

def test_delete_user(test_client, test_admin_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    delete_res = test_client.delete(f'/users/4/')
    assert delete_res.status_code == 200, 'Failed to delete test user'

    get_deleted_user_res = test_client.get(f'/users/4/')
    assert get_deleted_user_res.status_code == 404, 'Deleted user still exists in the database'


def test_role_based_read(
    test_client,
    test_admin_key,
    test_user_key,
    test_guest_key
) -> None:
    for i, key in enumerate([test_admin_key, test_user_key, test_guest_key]):
        test_client.cookies.set(AUTH_COOKIE_NAME, key)
        response = test_client.get('/users/')
        assert response.status_code == 200, f'User {i} was not able to get a user list'
        data = response.json().get('data')
        assert data is not None, f'Failed to get a user list for user {i}'
        expected_length = 3 - i
        assert len(data) == expected_length, f'User {i} was able to see more users than they should have'


def test_update_user(test_client, test_admin_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    
    create_res = test_client.post(
        '/users/',
        data={
            'username': 'test',
            'password': 'test',
            'role': 'user'
        }
    )
    assert create_res.status_code == 201, 'Failed to create test user for update test'
    
    update_data = {
        'username': 'test_user',
        'password': 'test',
        'role': 'admin'
    }

    update_res = test_client.patch(f'/users/4/', data=update_data)
    assert update_res.status_code == 202, 'Failed to update test user'

    updated_user = User(**update_res.json())

    assert updated_user.username == update_data['username'], 'Username was not updated correctly'
    assert updated_user.role == Role.ADMIN, 'Role was not updated correctly'

    update_data['username'] = 'admin'
    duplicate_username_res = test_client.patch(
        f'/users/4/',
        data=update_data
    )
    assert duplicate_username_res.status_code == 400, 'User was able to take existing username and break database integrity'



def test_user_me_route(test_client, test_admin_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    admin_me_res = test_client.get('/users/me/')
    assert admin_me_res.status_code == 200, 'Failed to get admin user data'
    admin_me_data = admin_me_res.json()
    
    admin_name = admin_me_data['username']
    assert admin_name == 'admin', 'Admin user data is incorrect'
    
    
    test_user_login = test_client.post(
        "/auth/login/",
        data={"username": 'test_user', "password": 'test'}
    )
    assert test_user_login.status_code == 200, 'Failed to login test user'
    
    test_client.cookies.set(AUTH_COOKIE_NAME, test_user_login.cookies[AUTH_COOKIE_NAME])
    test_user_me = test_client.get('/users/me/')
    test_username = test_user_me.json()['username']
    assert test_username == 'test_user', 'Test user data is incorrect' 


def test_read_user(test_client, test_admin_key, test_user_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    admin_me_res = test_client.get('/users/me/')
    
    assert admin_me_res.status_code == 200, 'Failed to get admin user data'
    
    admin_id = admin_me_res.json().get('id')
    
    test_client.cookies.set(AUTH_COOKIE_NAME, test_user_key)
    user_reads_admin = test_client.get(f'/users/{admin_id}/')
    assert user_reads_admin.status_code in (401, 403), 'User was able to read admin data'
    
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    
    admin_reads_admin = test_client.get(f'/users/{admin_id}/')
    assert admin_reads_admin.status_code == 200, 'Admin was not able to read their own data'
    
def test_details_read(test_client, test_admin_key) -> None:
    test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
    details_res = test_client.get('/users/details')
    
    assert details_res.status_code == 200, 'Failed to get user details'
    
    details_json = details_res.json().get('data')
    assert 'createdAt' in details_json[0], 'Created at field is missing'
    assert 'updatedAt' in details_json[0], 'Updated at field is missing'

