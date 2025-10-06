import httpx

from range_monitor.infra.adapters import AuthScheme, InvalidAPICredentials


async def get_saltstack_token(client: httpx.AsyncClient, credentials: dict) -> str:
    response = await client.post('/login', json={
        'eauth': 'pam',
        **credentials,
    })
    if response.status_code == 401 or response.status_code == 403:
        raise ValueError('Invalid credentials for SaltStack auth')

    response.raise_for_status()
    response_json: dict = response.json()

    returned = response_json.get('return')

    if not returned or len(returned) != 1:
        raise ValueError('Invalid response from SaltStack auth endpoint')

    if not (token := returned[0].get('token')):
        raise ValueError('No token found in SaltStack auth response')

    return token


class SaltstackAuthToken(AuthScheme):
    # Do tokens have a TTL?
    # Is there a refresh endpoint?
    # What kind of `static` immutable context per request
    # is needed?

    async def get_token(self, client: httpx.AsyncClient, credentials: dict) -> str:
        try:
            token = await get_saltstack_token(client, credentials)
        except Exception as exc:
            detail = 'Failed to obtain SaltStack token'
            if isinstance(exc, (httpx.HTTPStatusError, ValueError)):
                detail = str(exc)
            raise InvalidAPICredentials(detail) from exc

        return token

    def prepare_request(self, request: httpx.Request, token: str) -> None:
        request.headers['X-Auth-Token'] = token
