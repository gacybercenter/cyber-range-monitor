





from contextlib import asynccontextmanager

from fastapi import BackgroundTasks

from range_monitor.core.pydantic import PydanticMixin
from range_monitor.datasource.model import Guacamole
from range_monitor.datasource.schema.classes import ConnectionTestResponse
from range_monitor.datasource.service_abc import DatasourceService
from range_monitor.guac.services.client import guac_client


class GuacamoleCoreService(DatasourceService[Guacamole]):
    datasouce_orm = Guacamole


    async def enable_by_id(self, datasource_id: str) -> Guacamole:
        '''
        Enables the datasource with the given ID. If successful,
        any current connection is disconnected.

        Parameters
        ----------
        datasource_id : str

        Returns
        -------
        Guacamole
        '''
        enabled_guac = await super().enable_by_id(datasource_id)
        await guac_client.disconnect()
        return enabled_guac


    async def disable(self) -> None:
        '''
        Disables any currently enabled adapter and disconnects any current
        connection.
        '''
        await super().disable()
        await guac_client.disconnect()

    async def test_connection(
        self,
        bg_tasks: BackgroundTasks,
        guac_id: str | None = None,
    ) -> ConnectionTestResponse:
        '''
        Tests to see if a connection can be made to the datasource of the
        given ID or if none, the currently enabled datasource. If successful,
        a background task is added to delete the token.
        '''
        credentials = await self.get_credentials(guac_id)
        result = guac_client.create_client(
            credentials.adapter,
            credentials.password
        )
        if result.client:
            bg_tasks.add_task(result.client.delete_token)

        return ConnectionTestResponse(
            success=result.client is not None,
            error_message=result.error,
            is_enabled=credentials.adapter.enabled,
            datasource_id=credentials.adapter.id,
        )

    async def delete_datasource_id(self, datasource_id: str) -> None:
        was_enabled = guac_client.is_connected_datasource(datasource_id)
        await super().delete_datasource_id(datasource_id)
        if was_enabled:
            await guac_client.disconnect()

    async def update_datasource_id(
        self,
        datasource_id: str,
        update_body: PydanticMixin
    ) -> Guacamole:
        '''
        Updates the datasource with the given ID. If it is enabled and the
        connection is currently to that datasource, the connection is dropped
        till it is needed again.
        '''
        updated = await super().update_datasource_id(datasource_id, update_body)
        if updated.enabled and guac_client.is_connected_datasource(updated.id):
            await guac_client.disconnect() # reconnect next time an endpoint is touched
        return updated

    @asynccontextmanager
    async def session(self):
        if not guac_client.is_connected():
            enabled_credentials = await self.get_credentials()
            await guac_client.connect(
                enabled_credentials.adapter,
                enabled_credentials.password
            )

        async with guac_client.get_client() as session:
            yield session




