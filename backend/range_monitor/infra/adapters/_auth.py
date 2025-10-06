import abc
from collections.abc import AsyncGenerator
from typing import override

import httpx


class InvalidAPICredentials(Exception): ...


class AuthScheme(abc.ABC):

    @abc.abstractmethod
    async def get_token(self, client: httpx.AsyncClient, credentials: dict) -> str:
        '''
        Retrieves the token, returns None if no token is available.

        Parameters
        ----------
        client : APIClient | httpx.AsyncClient

        Returns
        -------
        str | None
        '''

    @abc.abstractmethod
    def prepare_request(
        self,
        request: httpx.Request,
        token: str
    ) -> None:
        '''
        Prepares the request by adding authentication details
        using the given token.

        Parameters
        ----------
        request : httpx.Request
        token : str

        Returns
        -------
        None
        '''

HTTPLifecycle = AsyncGenerator[httpx.Request, httpx.Response]

class APIAuthentication(httpx.Auth):
    '''
    An authentication scheme that uses an AuthScheme to
    obtain and refresh tokens as needed.

    Parameters
    ----------
    httpx
    '''

    def __init__(
        self,
        *,
        auth_client: httpx.AsyncClient,
        credentials: dict,
        scheme: AuthScheme,
    ) -> None:
        self._auth_client = auth_client
        self._credentials = credentials
        self.scheme = scheme

    @override
    async def async_auth_flow(self, request: httpx.Request) -> HTTPLifecycle:
        '''
        The async authentication flow that handles token
        retrieval and request preparation using the AuthScheme.

        Parameters
        ----------
        request : httpx.Request

        Returns
        -------
        HTTPLifecycle

        Yields
        ------
        Iterator[HTTPLifecycle]
        '''
        token = await self.scheme.get_token(
            self._auth_client,
            self._credentials
        )
        self.scheme.prepare_request(request, token)

        response = yield request

        if response.status_code != 401 or response.status_code != 403:
            return

        token = await self.scheme.get_token(
            self._auth_client,
            self._credentials
        )
        self.scheme.prepare_request(request, token)
        yield request

    async def kill(self) -> None:
        '''
        Closes the internal auth client if it's not already closed.
        '''
        if self._auth_client.is_closed:
            return

        await self._auth_client.aclose()

    async def authenticate(self) -> str:
        '''
        Authenticates using the provided credentials and returns
        the obtained token.

        Returns
        -------
        str
        '''
        return await self.scheme.get_token(self._auth_client, self._credentials)
