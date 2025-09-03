


from typing import Annotated
from fastapi import APIRouter, Depends
from range_monitor.params import TimestampParams, PageParams
from range_monitor.users.depends import authorization_required
from range_monitor.guac.depends import GuacCrudServiceDep
from range_monitor.guac.schema.datasource import GuacamoleListResponse

source_router = APIRouter(
    dependencies=[
        Depends(authorization_required)
    ]
)


@source_router.get(
    '/',
    response_model=GuacamoleListResponse,
)
async def list_guacamole_sources(
    timestamp_params: Annotated[
        TimestampParams,
        Depends(TimestampParams.depends)
    ],
    page_params: Annotated[
        PageParams,
        Depends(PageParams.depends)
    ],
    source_service: GuacCrudServiceDep,
) -> GuacamoleListResponse:


@source_router.post('/')
async def create_guacamole_source(): ...

@source_router.get('/{source_id}/')
async def get_guacamole_source(source_id: str): ...

@source_router.patch('/{source_id}/')
async def update_guacamole_source(source_id: str): ...

@source_router.get('/enabled/')
async def get_enabled_guacamole_source(): ...

