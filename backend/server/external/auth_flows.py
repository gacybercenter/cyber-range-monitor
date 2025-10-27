import abc
import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from datetime import timedelta
from typing import override

import httpx

logger = logging.getLogger(__name__)


class InvalidCredentialsError(Exception):
    '''
    Raised when API credentials are invalid.
    '''


class AuthFlow(abc.ABC):
    @abc.abstractmethod
    async def get_token(self, client: httpx.AsyncClient, credentials: dict) -> str:
        '''
        Retrieves the token, returns None if no token is available.

        Parameters
        ----------
        client : httpx.AsyncClient
            The HTTPX async client to use for the request.
        credentials : dict
            The credentials to use for obtaining the token.

        Returns
        -------
        str | None
        '''

    @abc.abstractmethod
    def prepare_request(self, request: httpx.Request, token: str) -> None:
        '''
        Prepares the request by adding authentication details
        using the given token.

        Parameters
        ----------
        request : httpx.Request
            The HTTPX request to prepare.
        token : str
            The authentication token to use.

        Returns
        -------
        None
        '''


class ClientAuth(httpx.Auth):
    '''
    Uses an auth flow to handle authentication for HTTPX requests.

    Parameters
    ----------
    httpx.Auth
    '''

    def __init__(
        self,
        *,
        auth_client: httpx.AsyncClient,
        credentials: dict,
        auth_flow: AuthFlow,
    ) -> None:
        self._auth_client = auth_client
        self._credentials = credentials
        self.scheme = auth_flow

    @override
    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        '''
        The async authentication flow that handles token
        retrieval and request preparation using the AuthScheme.

        Parameters
        ----------
        request : httpx.Request
            The HTTPX request to authenticate.

        Returns
        -------
        HTTPLifecycle

        Yields
        ------
        Iterator[HTTPLifecycle]
        '''
        token = await self.scheme.get_token(self._auth_client, self._credentials)
        self.scheme.prepare_request(request, token)

        response = yield request

        if response.status_code != 401 or response.status_code != 403:
            return

        token = await self.scheme.get_token(self._auth_client, self._credentials)
        self.scheme.prepare_request(request, token)
        yield request

    async def kill(self) -> None:
        """
        Closes the internal auth client if it's not already closed.
        """
        if self._auth_client.is_closed:
            return

        await self._auth_client.aclose()

    async def authenticate(self, *, credentials: dict | None = None) -> str:
        '''
        Authenticates using the provided credentials and returns
        the obtained token.

        Returns
        -------
        str
        '''
        credentials = credentials or self._credentials
        return await self.scheme.get_token(self._auth_client, credentials)


async def get_guac_token(client: httpx.AsyncClient, credentials: dict) -> str:
    response = await client.post(
        '/api/tokens',
        data=credentials,
    )
    response.raise_for_status()
    response_json: dict = response.json()
    if not (token := response_json.get('authToken')):
        logger.error('Failed to obtain guacamole token, response: %s', response_json)
        raise InvalidCredentialsError('Guacamole token not found in response')

    return token


async def get_saltstack_token(client: httpx.AsyncClient, credentials: dict) -> str:
    response = await client.post(
        '/login',
        json={
            'eauth': 'pam',
            **credentials,
        },
    )
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


class GuacamoleToken(AuthFlow):
    _IDLE_TIMEOUT = timedelta(minutes=5)

    def __init__(self) -> None:
        self._token: str | None = None
        self._last_used: float | None = None
        self._lock = asyncio.Lock()
        self._timeout = self._IDLE_TIMEOUT.total_seconds()

    def _ensure_token(self) -> None:
        '''
        NOTE: This method must be called within a lock

        Ensures the token is still valid based on idle timeout
        and clears it if it has expired.

        Returns
        -------
        str | None
        '''
        if self._last_used is None:
            return
        now = time.time()
        elapsed = now - self._last_used
        if elapsed > self._timeout:
            self._token = None
            self._last_used = None

    async def _refresh_token(self, client: httpx.AsyncClient, credentials: dict) -> str:
        try:
            self._token = await get_guac_token(client, credentials)
        except httpx.HTTPStatusError as exc:
            detail = 'Failed to obtain Guacamole token'
            if exc.response.status_code in (401, 403):
                detail = 'Invalid credentials for Guacamole auth'
            raise InvalidCredentialsError(detail) from exc

        self._last_used = time.time()
        return self._token

    async def get_token(self, client: httpx.AsyncClient, credentials: dict) -> str:
        async with self._lock:
            self._ensure_token()
            if self._token:
                self._last_used = time.time()
                return self._token
            return await self._refresh_token(client, credentials)

    def prepare_request(self, request: httpx.Request, token: str) -> None:
        request.url = request.url.copy_with(params={'token': token})

    @property
    def token(self) -> str | None:
        return self._token


class SaltstackAuthToken(AuthFlow):
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
            raise InvalidCredentialsError(detail) from exc

        return token

    def prepare_request(self, request: httpx.Request, token: str) -> None:
        request.headers['X-Auth-Token'] = token
