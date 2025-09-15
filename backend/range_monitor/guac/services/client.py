
from datetime import timedelta
from typing import Final, cast

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

    def update_token(self, new_token: str) -> None:
        if self._client is not None:
            self._client.token = new_token
            self._client.params['token'] = new_token


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
        self.update_token(cast(str, new_token))

guac_api: Final[_GuacamoleClient] = _GuacamoleClient()