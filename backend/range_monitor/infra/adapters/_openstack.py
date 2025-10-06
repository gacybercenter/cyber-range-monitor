import asyncio
import dataclasses as dc

from openstack import connection

from range_monitor.infra.adapters import utils as tenant_utils
from range_monitor.utils.decorators import asyncify


@dc.dataclass(slots=True)
class ConnectionCredentials:
    '''
    Dataclass representing the `auth` parameter for OpenStack SDK
    '''
    auth_url: str
    username: str
    password: str
    user_domain_name: str
    project_id: str | None = None
    project_domain_name: str | None = None
    project_name: str | None = None

    def get_kwargs(self) -> dict:
        auth = {
            'auth_url': self.auth_url,
            'username': self.username,
            'password': self.password,
            'user_domain_name': self.user_domain_name,
        }

        if self.project_id:
            auth['project_id'] = self.project_id

        if self.project_name:
            auth['project_name'] = self.project_name

        if self.project_domain_name:
            auth['project_domain_name'] = self.project_domain_name

        return auth


class InvalidOpenstackCredentials(Exception):
    pass

@asyncify()
def create_openstack_connection(
    *,
    credentials: ConnectionCredentials,
    region_name: str | None = None,
    identity_api_version: str = '3',
) -> connection.Connection:
    '''
    Creates and authorizes a new OpenStack connection.

    Parameters
    ----------
    credentials : ConnectionCredentials
    region_name : str | None, optional
    identity_api_version : str, optional

    Returns
    -------
    connection.Connection

    Raises
    ------
    InvalidOpenstackCredentials
        If the provided credentials are invalid or the connection cannot be
        established.
    '''
    auth = credentials.get_kwargs()
    conn = connection.Connection(
        region_name=region_name,
        auth=auth,
        identity_api_version=identity_api_version,
    )
    try:
        conn.authorize()
    except Exception as e:
        raise InvalidOpenstackCredentials(
            'Failed to authenticate with provided OpenStack credentials'
        ) from e

    return conn

@asyncify()
def close_openstack_connection(conn: connection.Connection) -> None:
    conn.close()


class OpenstackTenant:
    '''
    Manages an OpenStack connection, ensuring that only one connection is
    open at a time. This manages the context and connection lifecycle

    Raises
    ------
    InvalidOpenstackCredentials
        If the provided credentials are invalid or the connection cannot be
        established.
    '''
    __slots__ = ('_conn', '_lock', '_connected_hash')

    def __init__(self) -> None:
        self._conn: connection.Connection | None = None
        self._lock: asyncio.Lock = asyncio.Lock()
        self._connected_hash: bytes | None = None

    def get_connection(self) -> connection.Connection | None:
        return self._conn


    async def aclose(self) -> None:
        '''
        Closes the openstack tenant connection if one exists
        and clears the cached connection and hash.
        '''
        async with self._lock:
            if not self._conn:
                return
            await close_openstack_connection(self._conn)
            self._conn = None
            self._connected_hash = None

    async def aopen(
        self,
        *,
        credentials: ConnectionCredentials,
        region_name: str | None = None,
        identity_api_version: str = '3',
    ) -> connection.Connection:
        '''
        Opens a new OpenStack connection if one does not already exist with the
        same credentials.

        Parameters
        ----------
        credentials : ConnectionCredentials
        region_name : str | None, optional
        identity_api_version : str, optional

        Returns
        -------
        connection.Connection
        '''
        async with self._lock:
            cred_hash = tenant_utils.hash_dataclass(credentials)
            if self._conn and self._connected_hash == cred_hash:
                return self._conn

            if self._conn:
                await self.aclose()

            self._conn = await create_openstack_connection(
                credentials=credentials,
                region_name=region_name,
                identity_api_version=identity_api_version,
            )

            self._connected_hash = cred_hash

        return self._conn


    async def refresh_connection(self) -> None:
        '''
        Refreshes the current OpenStack connection by re-authorizing it.

        Raises
        ------
        InvalidOpenstackCredentials
            If there is no existing connection to refresh or if the
            re-authorization fails.
        '''
        async with self._lock:
            if not self._conn or not self._connected_hash:
                raise InvalidOpenstackCredentials(
                    'No existing connection to refresh'
                )
            try:
                self._conn.authorize()
            except Exception as e:
                await self.aclose()
                raise InvalidOpenstackCredentials(
                    'Failed to refresh connection, datasource credentials may be stale'
                ) from e

