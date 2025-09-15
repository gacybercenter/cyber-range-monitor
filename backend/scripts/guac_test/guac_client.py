




import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Coroutine

import httpx


class APIError(Exception):

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response

@dataclass
class GuacamoleConfig:
    host: str
    username: str
    password: str
    data_source: str
    retries: int = 3
    delay: float = 1.0

    @property
    def base_url(self) -> str:
        return f'{self.host}/api'

    @property
    def credentials(self) -> dict[str, str]:
        return {
            'username': self.username,
            'password': self.password,
        }

@asynccontextmanager
async def with_retries(
    *,
    retries: int = 3,
    delay: float = 1.0,
):
    attempt = 0
    while attempt < retries:
        try:
            yield
        except (
            httpx.RequestError,
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.ProxyError,
            httpx.RemoteProtocolError,
        ):
            attempt += 1
            if attempt >= retries:
                raise
            await asyncio.sleep(delay)
        except httpx.HTTPStatusError as e:
            raise APIError(
                f'API request failed with status code {e.response.status_code}.',
                status_code=e.response.status_code,
                response=e.response,
            )


async def get_json(
    client: httpx.AsyncClient,
    path: str,
    params: dict | None = None,
) -> dict:
    try:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise APIError(
            f'API request failed with status code {e.response.status_code}.',
            status_code=e.response.status_code,
            response=e.response,
        ) from e

async def post_json(
    client: httpx.AsyncClient,
    content: dict,
    params: dict | None = None,
) -> dict:
    try:
        response = await client.post(
            '/tokens',
            json=content,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise APIError(
            f'API request failed with status code {e.response.status_code}.',
            status_code=e.response.status_code,
            response=e.response,
        ) from e


class GuacamoleClient:
    def __init__(
        self,
        config: GuacamoleConfig,
        *,
        token: str | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=10.0,
        )
        if token is not None:
            self._client.params = {'token': token}

        self.auth = tokens(self._client)
        self.schema = schema(
            client=self._client,
            data_source=config.data_source,
        )
        self._config = config

    async def authenticate(self) -> str:
        token = await self.auth.create_token(
            username=self._config.username,
            password=self._config.password,
        )
        self._client.params = {'token': token}
        return token

class GucamoleNamesapce:

    def __init__(
        self,
        client: httpx.AsyncClient,
        config: GuacamoleConfig,
    ) -> None:
        self._client = client
        self._config = config

    @asynccontextmanager
    async def _wrap_request(self) :
        async with with_retries(
            retries=self._config.retries,
            delay=self._config.delay,
        ):
            yield

class tokens(GucamoleNamesapce):
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def create_token(
        self,
        *,
        username: str,
        password: str
    ) -> str:
        response = await self._client.post(
            '/tokens',
            json={
                'username': username,
                'password': password,
            }
        )
        response.raise_for_status()
        data: dict = response.json()
        if not (token := data.get('authToken')):
            raise APIError('Authentication response did not contain an authToken.')
        return token

    async def delete_token(self, token: str | None = None) -> None:
        if token is None:
            token = self._client.params.get('token')

        if token is None:
            raise ValueError('No token provided or set in client params.')

        async with self._wrap_request():
            response = await self._client.delete(f'/tokens/{token}')
            response.raise_for_status()





class schema(GucamoleNamesapce):

    @property
    def path(self) -> str:
        return f'/schema/{self._config.data_source}'


    async def list_user_attributes(self) -> dict:
        try:
            response = await self._client.get(
                f'{self.path}/userAttributes'
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise APIError(
                f'Failed to get user attributes with status code {e.response.status_code}.',
                status_code=e.response.status_code,
                response=e.response,
            ) from e

    async def list_user_group_attributes(self) -> dict:
        async with self._wrap_request():
            response = await self._client.get(f'{self.path}/userGroupAttributes')
            response.raise_for_status()
            return response.json()


    async def list_connection_attributes(self) -> dict:
        async with self._wrap_request():
            response = await self._client.get(f'{self.path}/connectionAttributes')
            response.raise_for_status()
            return response.json()

    