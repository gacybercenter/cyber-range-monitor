import abc
from typing import NamedTuple, TypeVar

import httpx
from openstack import connection

from server.external.api_clients import ApiClient, ClientContext
from server.external.auth_flows import InvalidCredentialsError
from server.external.openstack_client import (
    ConnectionCredentials,
    OpenstackClient,
    close_openstack_connection,
    create_openstack_connection,
)
from server.models import Guacamole, Openstack, Saltstack

D = TypeVar('D')
C = TypeVar('C')


class ConnectionTestDetail(NamedTuple):
    success: bool
    error: str | None


class DatasourceAdapter[D, C](abc.ABC):
    """
    An abstract base class defining the interface for
    external datasource adapter which can be used by a datasource service.

    Parameters
    ----------
    Generics :
        D : The datasource schema type.
        C : The connection type (e.g `httpx.AsyncClient`)
    """

    @abc.abstractmethod
    async def connect(self, datasource: D, password: str) -> C:
        """
        Establishes and returns a connection to the datasource.

        Parameters
        ----------
        datasource : D
            The datasource ORM.
        password : str
            The plaintext password for the datasource.

        Returns
        -------
        C
        """

    @abc.abstractmethod
    async def test_connection(self, datasource: D, password: str) -> ConnectionTestDetail:
        """
        Tests the connection to the datasource using the provided
        datasource details and password.

        Parameters
        ----------
        datasource : D
            The datasource ORM.
        password : str
            The plaintext password for the datasource.

        Returns
        -------
        bool
        """

    @abc.abstractmethod
    async def close_connection(self) -> None:
        """
        Closes the current connection to the datasource.
        """

    @abc.abstractmethod
    async def get_connection(self) -> C | None:
        """
        Retrieves the current connection if it exists.

        Returns
        -------
        C | None
        """


def create_guac_context(datasource: Guacamole, password: str) -> ClientContext:
    return ClientContext(
        datasource_id=datasource.id,
        state={
            'data_source_type': datasource.data_source_type,
            'hostname': datasource.hostname,
        },
        credentials={
            'username': datasource.username,
            'password': password,
        },
    )


def create_saltstack_context(saltstack: Saltstack, password: str) -> ClientContext:
    return ClientContext(
        datasource_id=saltstack.id,
        state={
            'hostname': saltstack.hostname,
            'endpoint': saltstack.endpoint,
        },
        credentials={
            'username': saltstack.username,
            'password': password,
        },
    )


def get_openstack_credentials(model: Openstack, password: str) -> ConnectionCredentials:
    return ConnectionCredentials(
        auth_url=model.auth_url,
        project_name=model.project_name,
        username=model.username,
        password=password,
        user_domain_name=model.user_domain_name,
        project_domain_name=model.project_domain_name,
    )


class GuacamoleAdapter(DatasourceAdapter[Guacamole, httpx.AsyncClient]):
    """
    The httpx.AsyncClient adapter for Guacamole datasources for it's
    RESTful API.
    """

    def __init__(self, tenant: ApiClient) -> None:
        self.tenant = tenant

    async def connect(self, datasource: Guacamole, password: str) -> httpx.AsyncClient:
        context = create_guac_context(datasource, password)
        connection = await self.tenant.connect(
            base_url=datasource.hostname,
            context=context,
        )
        await self.tenant.authenticate()
        return connection

    async def test_connection(
        self, datasource: Guacamole, password: str
    ) -> ConnectionTestDetail:
        context = create_guac_context(datasource, password)
        try:
            await self.tenant.try_credentials(
                base_url=datasource.hostname, context=context
            )
        except InvalidCredentialsError:
            return ConnectionTestDetail(
                success=False, error='Invalid credentials for Guacamole auth'
            )
        except httpx.HTTPError as exc:
            return ConnectionTestDetail(
                success=False, error=f'HTTP error during Guacamole auth: {exc!s}'
            )

        return ConnectionTestDetail(success=True, error=None)

    async def close_connection(self) -> None:
        await self.tenant.aclose()

    async def get_connection(self) -> httpx.AsyncClient | None:
        return self.tenant.get_client()


class SaltstackAdapter(DatasourceAdapter[Saltstack, httpx.AsyncClient]):
    """
    The httpx.AsyncClient adapter for Saltstack datasources for it's
    RESTful API.
    """

    _SALT_PORT = 8000  # is this always the port?

    def __init__(self, tenant: ApiClient) -> None:
        self.tenant = tenant

    async def connect(self, datasource: Saltstack, password: str) -> httpx.AsyncClient:
        base_url = httpx.URL(datasource.hostname, port=self._SALT_PORT)
        context = create_saltstack_context(datasource, password)
        connection = await self.tenant.connect(
            context=context,
            base_url=base_url,
        )

        await self.tenant.authenticate()
        return connection

    async def test_connection(
        self, datasource: Saltstack, password: str
    ) -> ConnectionTestDetail:
        context = create_saltstack_context(datasource, password)
        base_url = httpx.URL(
            datasource.hostname,
            port=self._SALT_PORT,
        )
        try:
            await self.tenant.try_credentials(base_url=base_url, context=context)
        except InvalidCredentialsError as exc:
            return ConnectionTestDetail(success=False, error=str(exc))
        except Exception as exc:
            return ConnectionTestDetail(
                success=False, error=f'Error during Saltstack auth: {exc!s}'
            )

        return ConnectionTestDetail(success=True, error=None)

    async def close_connection(self) -> None:
        await self.tenant.aclose()

    async def get_connection(self) -> httpx.AsyncClient | None:
        return self.tenant.get_client()


class OpenstackAdapter(DatasourceAdapter[Openstack, connection.Connection]):
    """
    The Openstack connection adapter for Openstack datasources using the
    openstacksdk
    """

    def __init__(self, context: OpenstackClient) -> None:
        self.tenant: OpenstackClient = context

    async def connect(
        self, datasource: Openstack, password: str
    ) -> connection.Connection:
        creds = get_openstack_credentials(datasource, password)
        return await self.tenant.aopen(
            credentials=creds,
            region_name=datasource.region_name,
            identity_api_version=datasource.identity_api_version,
        )

    async def test_connection(
        self, datasource: Openstack, password: str
    ) -> ConnectionTestDetail:
        try:
            temp_connection = await create_openstack_connection(
                credentials=get_openstack_credentials(datasource, password),
                region_name=datasource.region_name,
                identity_api_version=datasource.identity_api_version,
            )
            await close_openstack_connection(temp_connection)
        except Exception:
            return ConnectionTestDetail(
                success=False, error='Invalid credentials for Openstack auth'
            )

        return ConnectionTestDetail(success=True, error=None)

    async def close_connection(self) -> None:
        await self.tenant.aclose()

    async def get_connection(self) -> connection.Connection | None:
        return self.tenant.get_connection()
