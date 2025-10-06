from openstack import connection

from range_monitor.infra.adapters._openstack import (
    ConnectionCredentials,
    OpenstackTenant,
    close_openstack_connection,
    create_openstack_connection,
)
from range_monitor.sources._adapter_abc import (
    APISourceAdapter,
    ConnectionTestDetail,
)
from range_monitor.sources.models import Openstack


def get_model_credentials(model: Openstack, password: str) -> ConnectionCredentials:
    return ConnectionCredentials(
        auth_url=model.auth_url,
        project_name=model.project_name,
        username=model.username,
        password=password,
        user_domain_name=model.user_domain_name,
        project_domain_name=model.project_domain_name,
    )


class OpenstackAdapter(APISourceAdapter[Openstack, connection.Connection]):

    def __init__(self, context: OpenstackTenant) -> None:
        self.tenant: OpenstackTenant = context

    async def connect(
        self,
        datasource: Openstack,
        password: str
    ) -> connection.Connection:
        creds = get_model_credentials(datasource, password)
        return await self.tenant.aopen(
            credentials=creds,
            region_name=datasource.region_name,
            identity_api_version=datasource.identity_api_version,
        )

    async def test_connection(
        self,
        datasource: Openstack,
        password: str
    ) -> ConnectionTestDetail:

        try:
            temp_connection = await create_openstack_connection(
                credentials=get_model_credentials(datasource, password),
                region_name=datasource.region_name,
                identity_api_version=datasource.identity_api_version,
            )
            await close_openstack_connection(temp_connection)
        except Exception:
            return ConnectionTestDetail(
                success=False,
                error='Invalid credentials for Openstack auth'
            )

        return ConnectionTestDetail(
            success=True,
            error=None
        )

    async def close_connection(self) -> None:
        await self.tenant.aclose()

    async def get_connection(self) -> connection.Connection | None:
        return self.tenant.get_connection()
