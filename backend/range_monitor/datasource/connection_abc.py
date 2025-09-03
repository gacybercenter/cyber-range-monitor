



import abc
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Generic, NamedTuple, TypeVar

import anyio
import anyio.to_thread

from range_monitor.datasource.model import Datasource
from range_monitor.errors import DatasourceConnectionError

C = TypeVar('C')
D = TypeVar('D', bound=Datasource)

class ConnectionResult(NamedTuple, Generic[C]):
    client: C | None
    error: str | None


class DatasourceConnection(abc.ABC, Generic[C, D]):
    _lock: asyncio.Lock = asyncio.Lock()
    _connected_id: str | None = None
    _client: C | None = None
    _last_seen: float = 0.0
    idle_timeout: timedelta = timedelta(minutes=5) # default to 5 minutes


    @property
    def client(self) -> C:
        if self._client is None:
            raise DatasourceConnectionError(
                'datasource',
                'No active connection'
            )
        return self._client


    async def disconnect(self) -> None:
        async with self._lock:
            self._client = None
            self._connected_id = None
            self._last_seen = 0.0

    def is_connected_datasource(self, datasource_id: str) -> bool:
        return self._connected_id == datasource_id

    def is_connected(self) -> bool:
        return self._client is not None

    @classmethod
    @abc.abstractmethod
    def create_client(cls, datasource: D, password: str) -> ConnectionResult[C]: ...

    @abc.abstractmethod
    async def refresh_auth(self) -> None: ...


    async def connect(self, datasource: D, password: str) -> None:
        async with self._lock:
            if not datasource.enabled:
                raise DatasourceConnectionError(
                    'datasource',
                    'Datasource is disabled'
                )
            result = await anyio.to_thread.run_sync(
                self.create_client,
                datasource,
                password
            )
            if result.error or result.client is None:
                raise DatasourceConnectionError(
                    'datasource',
                    result.error or 'Unknown error'
                )
            self._client = result.client
            self._connected_id = datasource.id # type: ignore
            self._last_seen = time.time()

    @asynccontextmanager
    async def get_client(self):
        if self.is_stale():
            async with self._lock:
                await self.refresh_auth()
        try:
            yield self.client
        finally:
            async with self._lock:
                self._last_seen = time.time()

    async def is_stale(self) -> bool:
        '''
        Checks if the current connection is stale based on
        idle timeout.

        Returns
        -------
        bool
        '''
        if self._client is None:
            return True

        now = time.time()
        timeout_secs = self.idle_timeout.total_seconds()
        return (now - self._last_seen) > timeout_secs

