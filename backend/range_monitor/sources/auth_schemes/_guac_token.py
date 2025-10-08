import asyncio
import logging
import time
from datetime import timedelta

import httpx

from range_monitor.infra.adapters import AuthScheme, InvalidAPICredentials

logger = logging.getLogger(__name__)


async def get_guac_token(client: httpx.AsyncClient, credentials: dict) -> str:
    response = await client.post(
        '/api/tokens',
        data=credentials,
    )
    response.raise_for_status()
    response_json: dict = response.json()
    if not (token := response_json.get('authToken')):
        logger.error('Failed to obtain guacamole token, response: %s', response_json)
        raise InvalidAPICredentials()
    return token


class GuacamoleAuth(AuthScheme):
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
            return None
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
            raise InvalidAPICredentials(detail) from exc

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