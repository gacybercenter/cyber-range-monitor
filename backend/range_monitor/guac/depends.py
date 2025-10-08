from typing import Annotated

from fastapi import Depends

from range_monitor.guac.service import GuacamoleAPIService
from range_monitor.sources.depends import GuacamoleServiceDep, GuacTenantDep


async def get_guacamole_api_service(
    tenant: GuacTenantDep,
    guac_service: GuacamoleServiceDep
) -> GuacamoleAPIService:

    api_client = await guac_service.get_connection()
    context = tenant.get_context()
    assert context is not None
    return GuacamoleAPIService(
        client=api_client,
        data_source=context.state['data_source_type']
    )


GuacAPIServiceDep = Annotated[GuacamoleAPIService, Depends(get_guacamole_api_service)]