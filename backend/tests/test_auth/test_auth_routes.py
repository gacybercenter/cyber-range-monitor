from datetime import datetime, timezone, timedelta
import re
import pytest


from app.auth.const import AUTH_COOKIE_NAME
from app import config
from fastapi.testclient import TestClient


def test_credentials(test_admin_key: str) -> None:
    assert test_admin_key is not None, 'The api_key is None for admin when it should be present in response'


def test_revoked_key(test_admin_key: str, test_client: TestClient) -> None:
    response = test_client.post(
        '/auth/logout',
        cookies={AUTH_COOKIE_NAME: test_admin_key}
    )
    response = test_client.get('/logs/today/', cookies={
        AUTH_COOKIE_NAME: test_admin_key
    })
    assert response.status_code == 401, 'Session was not revoked after logout'


@pytest.mark.asyncio
async def test_rbac(
    test_guest_key: str,
    test_user_key: str,
    test_client: TestClient
) -> None:
    details_res = test_client.get(
        '/users/details/',
        cookies={AUTH_COOKIE_NAME: test_guest_key}
    )
    assert details_res.status_code > 400, 'read only user was able to read user details when it should be allowed'

    read_all_res = test_client.get(
        '/users/1',
        cookies={AUTH_COOKIE_NAME: test_guest_key}
    )
    assert read_all_res.status_code > 400, 'read only user was able to read an admin when it should not be allowed'

    details_res = test_client.get(
        '/users/1',
        cookies={AUTH_COOKIE_NAME: test_user_key}
    )
    assert details_res.status_code > 400, 'guest user was able to read an admin when it should not be allowed'


def test_api_key_cookie(test_client: TestClient) -> None:
    cookie_expr = config.get_api_key_config().client_key_lifetime()

    response = test_client.post('/auth/login/', data={
        'username': 'admin',
        'password': 'admin'
    })
    assert response.status_code == 200, 'Login failed for a valid user'

    now = datetime.now(timezone.utc)
    set_cookie_hdr = response.headers.get('Set-Cookie')
    assert set_cookie_hdr is not None, 'API key cookie not found in response'
    max_age = re.search(r'max-age=(\d+)', set_cookie_hdr)
    if max_age:
        exp_time = int(max_age.group(1))
        time_diff = abs(exp_time - cookie_expr)
        expected_exp_time = now + timedelta(seconds=cookie_expr)
        assert time_diff < 5, 'API key cookie max-age does not match expected value'
    else:
        exprs_match = re.search(r"Expires=([^;]+)", set_cookie_hdr)
        assert exprs_match is not None, 'API key cookie expiration not found in response'

        exprs_str = exprs_match.group(1)
        exp_time = datetime.strptime(exprs_str, '%a, %d-%b-%Y %H:%M:%S GMT')

        expected_exp_time = now + timedelta(seconds=cookie_expr)

        time_diff = abs((exp_time - expected_exp_time).total_seconds())
    assert time_diff < 5, 'API key cookie expiration does not match expected value ' \
        f'and expires sooner or later than it should. \nExpires At:{exprs_str}\nExpected: {expected_exp_time}'


def test_deleted_user_key(test_admin_key: str, test_client: TestClient) -> None:
    sample_data = {
        'username': 'test',
        'password': 'test',
        'role': 'user'
    }
    create_res = test_client.post(
        '/users/',
        data=sample_data,
        cookies={ 
            AUTH_COOKIE_NAME: test_admin_key
        }
    )
    assert create_res.status_code == 201, 'Failed to create a test user'

    del sample_data['role']
    login_res = test_client.post(
        '/auth/login/',
        data=sample_data
    )

    assert login_res.status_code == 200, 'Failed to login as the test user'

    api_key = login_res.cookies.get(AUTH_COOKIE_NAME)
    assert api_key is not None, 'The api_key is None for the test user when it should be present in response'

    test_user_id = create_res.json().get('id')
    delete_res = test_client.delete(
        f'/users/{test_user_id}/',
        cookies={AUTH_COOKIE_NAME: test_admin_key}
    )
    assert delete_res.status_code == 200, 'Failed to delete the test user'

    me_res = test_client.get(
        '/users/me/',
        cookies={AUTH_COOKIE_NAME: api_key}
    )
    assert me_res.status_code > 400, 'Deleted users api key was still valid.'





