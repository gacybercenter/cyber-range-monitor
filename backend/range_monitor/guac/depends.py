from typing import Annotated

from fastapi import Depends

from range_monitor.guac.api import GuacamoleAPI
from range_monitor.guac.service import GuacamoleAPIService
from range_monitor.sources.depends import GuacamoleServiceDep, GuacTenantDep


async def get_guacamole_api(
    tenant: GuacTenantDep,
    guac_service: GuacamoleServiceDep
) -> GuacamoleAPI:

    api_client = await guac_service.get_connection()
    context = tenant.get_context()
    assert context is not None
    return GuacamoleAPI(
        client=api_client,
        data_source=context.state['data_source_type']
    )


GuacAPIDep = Annotated[GuacamoleAPI, Depends(get_guacamole_api)]


async def get_guacamole_api_service(api: GuacAPIDep) -> GuacamoleAPIService:
    return GuacamoleAPIService(
        api=api
    )

GuacAPIServiceDep = Annotated[GuacamoleAPIService, Depends(get_guacamole_api_service)]