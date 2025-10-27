from typing import Annotated

from fastapi import Depends

from server.app.data_sources.depends import GuacamoleServiceDep, GuacTenantDep
from server.app.guac.client.spec import GuacamoleAPISpec
from server.app.guac.services.core import GuacamoleRestService


async def get_guacamole_client_spec(
    tenant: GuacTenantDep, guac_service: GuacamoleServiceDep
) -> GuacamoleAPISpec:
    api_client = await guac_service.get_connection()
    context = tenant.c
    assert context is not None
    return GuacamoleAPISpec.create(
        client=api_client,
        data_source=context.state['data_source_type'],  # type: ignore
    )


GuacClientSpecDep = Annotated[GuacamoleAPISpec, Depends(get_guacamole_client_spec)]


async def get_guacamole_rest_service(spec: GuacClientSpecDep) -> GuacamoleRestService:
    return GuacamoleRestService(spec)


GuacRestServiceDep = Annotated[GuacamoleRestService, Depends(get_guacamole_rest_service)]
