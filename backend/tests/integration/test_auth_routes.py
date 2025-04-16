import time
from unittest.mock import patch
import pytest

from fastapi.testclient import TestClient
import test


AUTH_ROUTE = '/users/me/'
ADMIN_ROUTE = '/users/details'

LOGIN = '/auth/'
LOGOUT = '/auth/logout/'

SERVICE_MODULE = 'app.auth.service'


@pytest.mark.integration
class TestAuthRouter:
    def test_login_route(self, test_client: TestClient) -> None:
        valid_login = test_client.post(
            LOGIN,
            json={'username': 'admin', 'password': 'admin'}
        )
        assert valid_login.status_code == 200, (
            'Credentials for admin which are known to work were rejected.'
        )

        api_key = valid_login.json().get("apiKey")

        assert api_key is not None, 'API key was not returned in the response'

        test_req = test_client.get(
            '/users/details',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        assert test_req.status_code == 200, 'Request with valid cookie failed'

        bad_login = test_client.post(
            '/auth/',
            json={'username': 'admin', 'password': 'bad_password'}
        )
        assert bad_login.status_code != 200, 'Credentials for admin which are known to work were rejected.'

    def test_logout_route(self, test_admin_client: TestClient) -> None:
        logout = test_admin_client.post('/auth/logout/')
        assert logout.status_code == 200, 'Logout failed'

        test_req = test_admin_client.get(
            '/users/details'
        )
        assert test_req.status_code != 200, 'Request with invalid authorization succeeded'

    @patch(f'{SERVICE_MODULE}.KEY_EXPIRATION', 5)
    def test_key_expiring(self, test_client: TestClient) -> None:

        login = test_client.post(
            LOGIN,
            json={'username': 'admin', 'password': 'admin'}
        )
        auth = {'Authorization': f'Bearer {login.json().get("apiKey")}'}
        res = test_client.get(
            '/users/details',
            headers=auth
        )
        assert res.status_code == 200, 'Request with valid key failed'
        time.sleep(6)
        res = test_client.get(
            '/users/details',
            headers=auth
        )

        assert res.status_code != 200, 'Request with expired key succeeded'

    @patch(f'{SERVICE_MODULE}.KEY_EXPIRATION', 5)
    def test_key_max_age_reached(self, test_client: TestClient) -> None:

        login = test_client.post(
            LOGIN,
            json={'username': 'admin', 'password': 'admin'}
        )
        auth = {'Authorization': f'Bearer {login.json().get("apiKey")}'}
        res = test_client.get(
            '/users/details',
            headers=auth
        )
        assert res.status_code == 200, 'Request with valid key failed'
        time.sleep(6)
        res = test_client.get(
            '/users/details',
            headers=auth
        )

        assert res.status_code != 200, 'Request with expired key succeeded'

    def test_key_hijack_prevent(self, test_admin_client: TestClient) -> None:
        test_admin_client.headers.update({
            'user-agent': 'not-original',
        })
        res = test_admin_client.get(
            '/users/details'
        )
        assert res.status_code != 200, 'Request with hijacked key (different identity) succeeded'

    
    
    
    
    