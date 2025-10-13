
import dataclasses as dc
from typing import Self

import httpx

# keep in mind, the range_monitor (unless scope has changed),
# should be primarily read-only

@dc.dataclass(slots=True)
class GuacamoleAPISpec:
    '''
    Contains the RESTful Guacamole API client context
    and URL endpoints.
    '''
    client: httpx.AsyncClient
    data_source: str
    sessions_url: str

    @property
    def tunnels(self) -> str:
        return '/api/session/tunnels'

    @property
    def history(self) -> str:
        return f'{self.sessions_url}/history'

    @property
    def users(self) -> str:
        return f'{self.sessions_url}/users'

    @property
    def connections(self) -> str:
        return f'{self.sessions_url}/connections'

    @property
    def connection_groups(self) -> str:
        return f'{self.sessions_url}/connectionGroups'

    @property
    def usergroups(self) -> str:
        return f'{self.sessions_url}/userGroups'

    @property
    def sharing_profiles(self) -> str:
        return f'{self.sessions_url}/sharingProfiles'

    @property
    def active_connections(self) -> str:
        return f'{self.sessions_url}/activeConnections'

    @property
    def client_token(self) -> str:
        '''
        See `range_monitor.sources.auth_schemes._guac_token`
        for full type definition.

        Returns
        -------
        str
        '''
        return self.client.auth.scheme.token  # type: ignore

    @property
    def base_url(self) -> str:
        return str(self.client.base_url)

    @classmethod
    def create(
        cls,
        client: httpx.AsyncClient,
        data_source: str = 'default',
    ) -> Self:
        sessions_url = f'/api/session/data/{data_source}'
        return cls(
            client=client,
            data_source=data_source,
            sessions_url=sessions_url
        )




