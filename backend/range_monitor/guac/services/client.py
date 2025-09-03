
from datetime import timedelta
from typing import Final

import anyio
import anyio.to_thread
import guacamole

from range_monitor.datasource.connection_abc import (
    ConnectionResult,
    DatasourceConnection,
    DatasourceConnectionError,
)
from range_monitor.datasource.model import Guacamole


class _GuacamoleClient(DatasourceConnection[guacamole.session, Guacamole]):
    idle_timeout: timedelta = timedelta(minutes=5)

    @classmethod
    def create_client(
        cls,
        datasource: Guacamole,
        password: str
    ) -> ConnectionResult[guacamole.session]:
        try:
            session = guacamole.session(
                host=datasource.host,
                username=datasource.username,
                password=password,
                data_source=datasource.data_source,
            )
        except KeyError:
            return ConnectionResult(
                client=None,
                error='Invalid datasource credentials or hostname.'
            )

        return ConnectionResult(client=session, error=None)


    async def refresh_auth(self) -> None:
        '''
        Refreshes the authentication token for the current session.

        Raises
        ------
        DatasourceConnectionError
            _If the token refresh fails_
        '''
        try:
            new_token = await anyio.to_thread.run_sync(
                self.client.generate_token
            )
        except KeyError:
            await self.disconnect()
            raise DatasourceConnectionError(
                'guacamole',
                'Failed to refresh session token, datasource credentials may be stale',
            )
        self._client.token = new_token # type: ignore
        self._client.params['token'] = new_token # type: ignore

guac_client: Final[_GuacamoleClient] = _GuacamoleClient()