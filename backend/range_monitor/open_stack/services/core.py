


from contextlib import asynccontextmanager

from range_monitor.core.pydantic import PydanticMixin
from range_monitor.datasource.model import OpenStack
from range_monitor.datasource.schema import ConnectionTestResponse
from range_monitor.datasource.service_abc import DatasourceService
from range_monitor.open_stack.services.client import openstack_client


class OpenstackCoreService(DatasourceService[OpenStack]):
    datasouce_orm = OpenStack


    async def test_connection(
        self,
        datasource_id: str | None = None,
    ) -> ConnectionTestResponse:

        credentials = await self.get_credentials(datasource_id)

        result = openstack_client.create_client(
            credentials.adapter,
            credentials.password
        )

        return ConnectionTestResponse(
            success=result.client is not None,
            is_enabled=credentials.adapter.enabled,
            error_message=result.error,
            datasource_id=credentials.adapter.id,
        )


    async def enable_by_id(self, datasource_id: str) -> OpenStack:
        enabled = await super().enable_by_id(datasource_id)
        await openstack_client.disconnect()
        return enabled

    async def disable(self) -> None:
        await super().disable()
        await openstack_client.disconnect()

    async def update_datasource_id(
        self,
        datasource_id: str,
        update_body: PydanticMixin
    ) -> OpenStack:
        updated = await super().update_datasource_id(datasource_id, update_body)
        if updated.enabled and openstack_client.is_connected_datasource(updated.id):
            await openstack_client.disconnect()

        return updated

    async def delete_datasource_id(self, datasource_id: str) -> None:
        was_active = openstack_client.is_connected_datasource(datasource_id)
        await super().delete_datasource_id(datasource_id)
        if was_active:
            await openstack_client.disconnect()

    @asynccontextmanager
    async def connection(self):
        if not openstack_client.is_connected():
            enabled_credentials = await self.get_credentials()
            await openstack_client.connect(
                enabled_credentials.adapter,
                enabled_credentials.password
            )

        async with openstack_client.get_client() as client:
            yield client