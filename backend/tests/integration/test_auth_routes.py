from fastapi.testclient import TestClient

import pytest


import pytest


@pytest.mark.asynciotest_user_client
class TestAuthIntegration:
    def test_login_route(self, test_client: TestClient) -> None:
        valid_login = test_client.post(
            '/auth/',
            data={'username': 'admin', 'password': 'admin'}
        )
        assert valid_login.status_code == 200, 'Credentials for admin which are known to work were rejected.'

        api_key = valid_login.json().get("apiKey")

        assert api_key
    
        test_req = test_client.get(
            '/users/details',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        assert test_req.status_code == 200, 'Request with valid cookie failed'

        bad_login = test_client.post(
            '/auth/',
            data={'username': 'admin', 'password': 'bad_password'}
        )
        assert bad_login.status_code != 200, 'Credentials for admin which are known to work were rejected.'

    def test_logout_route(self, test_admin_client: TestClient) -> None:
        logout = test_admin_client.post('/auth/logout/')
        assert logout.status_code == 200, 'Logout failed'

        test_req = test_admin_client.get(
            '/users/details'
        )
        assert test_req.status_code != 200, 'Request with invalid cookie succeeded'

