import asyncio
import time
from fastapi.testclient import TestClient

import pytest

from app.auth.const import AUTH_COOKIE_NAME

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
class TestAuthIntegration:
    def test_login_route(self, test_client: TestClient) -> None:
        valid_login = test_client.post(
            '/auth/login/',
            data={'username': 'admin', 'password': 'admin'}
        )
        assert valid_login.status_code == 200, 'Credentials for admin which are known to work were rejected.'
        api_key = valid_login.cookies.get(AUTH_COOKIE_NAME)
        assert api_key is not None, 'Cookie was not set'

        test_req = test_client.get(
            '/users/details',
            cookies={AUTH_COOKIE_NAME: api_key}
        )
        assert test_req.status_code == 200, 'Request with valid cookie failed'

        bad_login = test_client.post(
            '/auth/login/',
            data={'username': 'admin', 'password': 'bad_password'}
        )
        assert bad_login.status_code != 200, 'Credentials for admin which are known to work were rejected.'
        assert bad_login.cookies.get(
            AUTH_COOKIE_NAME) is None, 'Cookie was set for invalid credentials'

    def test_logout_route(self, test_client: TestClient, test_admin_key: str) -> None:
        test_client.cookies.set(AUTH_COOKIE_NAME, test_admin_key)
        logout = test_client.post('/auth/logout/')
        assert logout.status_code == 200, 'Logout failed'
        assert logout.cookies.get(
            AUTH_COOKIE_NAME) is None, 'Cookie was not cleared'

        test_req = test_client.get(
            '/users/details',
            cookies={AUTH_COOKIE_NAME: test_admin_key}
        )
        assert test_req.status_code != 200, 'Request with invalid cookie succeeded'

    def test_api_key_expiration(self, test_client: TestClient) -> None:
        mock_config = MagicMock()
        mock_config.key_max_age.return_value = 2  # 2 seconds
        mock_config.cookie_exp.return_value = 4   # 4 seconds

        with patch("app.auth.service.auth_conf", mock_config), \
                patch("app.auth.api_key_store.auth_conf", mock_config):

            login_response = test_client.post(
                '/auth/login/',
                data={'username': 'admin', 'password': 'admin'}
            )
            assert login_response.status_code == 200

            api_key = login_response.cookies.get(AUTH_COOKIE_NAME)
            assert api_key is not None

            test_client.cookies.set(AUTH_COOKIE_NAME, api_key)
            initial_request = test_client.get('/users/details')
            assert initial_request.status_code == 200

            time.sleep(4)

            expired_request = test_client.get('/users/details/')
            assert expired_request.status_code in (401, 403)
