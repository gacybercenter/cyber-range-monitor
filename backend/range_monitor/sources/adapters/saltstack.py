import httpx

from range_monitor.sources._adapter_abc import (
    APISourceAdapter,
    ConnectionTestDetail,
)
from range_monitor.sources.models import Saltstack
from range_monitor.infra.tenants import APITenant, InvalidAPICredentials, TenantContext


def get_saltstack_context(Saltstack: Saltstack, password: str) -> TenantContext:
    return TenantContext(
        datasource_id=Saltstack.id,
        state={
            'hostname': Saltstack.hostname,
            'endpoint': Saltstack.endpoint,
        },
        credentials={
            'username': Saltstack.username,
            'password': password,
        }
    )



class SaltstackAdapter(APISourceAdapter[Saltstack, httpx.AsyncClient]):
    _SALT_PORT = 8000 # is this always the port?


    def __init__(self, tenant: APITenant) -> None:
        self.tenant = tenant

    async def connect(self, datasource: Saltstack, password: str) -> httpx.AsyncClient:
        base_url = httpx.URL(
            datasource.hostname,
            port=self._SALT_PORT
        )
        context = get_saltstack_context(datasource, password)
        connection = await self.tenant.aconnect(
            context=context,
            base_url=base_url,
        )
        await self.tenant.authenticate()
        return connection

    async def test_connection(
        self,
        datasource: Saltstack,
        password: str
    ) -> ConnectionTestDetail:
        context = get_saltstack_context(datasource, password)
        base_url = httpx.URL(
            datasource.hostname,
            port=self._SALT_PORT,
        )
        async with self.tenant.auth_scheme(base_url, context) as scheme:
            try:
                await scheme.authenticate()
            except InvalidAPICredentials as exc:
                return ConnectionTestDetail(
                    success=False,
                    error=str(exc)
                )

        return ConnectionTestDetail(
            success=True,
            error=None
        )

    async def close_connection(self) -> None:
        await self.tenant.adisconnect()

    async def get_connection(self) -> httpx.AsyncClient | None:
        return self.tenant.get_client()