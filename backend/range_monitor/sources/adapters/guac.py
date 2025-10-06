import httpx

from range_monitor.infra.adapters import APITenant, InvalidAPICredentials, TenantContext
from range_monitor.sources._adapter_abc import (
    APISourceAdapter,
    ConnectionTestDetail,
)
from range_monitor.sources.models import Guacamole


def _get_client_context(datasource: Guacamole, password: str) -> TenantContext:
    return TenantContext(
        datasource_id=datasource.id,
        state={
            'data_source_type': datasource.data_source_type,
            'hostname': datasource.hostname,
        },
        credentials={
            'username': datasource.username,
            'password': password,
        }
    )


class GuacamoleAdapter(APISourceAdapter[Guacamole, httpx.AsyncClient]):

    def __init__(self, tenant: APITenant) -> None:
        self.tenant = tenant

    async def connect(self, datasource: Guacamole, password: str) -> httpx.AsyncClient:
        context = _get_client_context(datasource, password)
        connection = await self.tenant.aconnect(
            base_url=datasource.hostname,
            context=context,
        )
        await self.tenant.authenticate()
        return connection

    async def test_connection(
        self,
        datasource: Guacamole,
        password: str
    ) -> ConnectionTestDetail:
        context = _get_client_context(datasource, password)
        async with self.tenant.auth_scheme(datasource.hostname, context) as scheme:
            try:
                await scheme.authenticate()
            except InvalidAPICredentials:
                return ConnectionTestDetail(
                    success=False,
                    error='Invalid credentials for Guacamole auth'
                )

        return ConnectionTestDetail(
            success=True,
            error=None
        )

    async def close_connection(self) -> None:
        await self.tenant.adisconnect()

    async def get_connection(self) -> httpx.AsyncClient | None:
        return self.tenant.get_client()
