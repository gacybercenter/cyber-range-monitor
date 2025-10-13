import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from range_monitor.auth.depends import AdminRequired, UserRequired
from range_monitor.schema.params import PageParamsDep
from range_monitor.sources.depends import GuacamoleServiceDep
from range_monitor.sources.schemas import (
    CreateGuacamoleBody,
    GuacamolePage,
    GuacamoleSchema,
)
from range_monitor.utils.openapi_extra import Error
from range_monitor.utils.response_class import MsgspecJsonResponse

guac_router = APIRouter()

GuacamoleInstance = Annotated[
    uuid.UUID,
    Path(
        ...,
        description='The UUID of the Guacamole instance',
    ),
]

SourceLabel = Annotated[str, Query(description='Filter datasources by label')]


@guac_router.get(
    '/',
    response_model=GuacamolePage,
    dependencies=[Depends(UserRequired)],
)
async def list_guacamole_sources(
    guac_service: GuacamoleServiceDep,
    page: PageParamsDep,
    label: SourceLabel | None = None,
) -> GuacamolePage:
    """
    Retrieve a paginated list of Guacamole datasources.
    """
    return await guac_service.list_datasources(label, page)


@guac_router.post(
    '/',
    response_model=GuacamoleSchema,
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    },
)
async def create_guacamole_source(
    guac_data: Annotated[CreateGuacamoleBody, Body(...)],
    guac_service: GuacamoleServiceDep,
) -> GuacamoleSchema:
    """
    Create a new Guacamole datasource.
    """
    model = await guac_service.create_source(guac_data)
    return guac_service.serialize(model)


@guac_router.get(
    '/{guac_id}',
    response_model=GuacamoleSchema,
    dependencies=[Depends(UserRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Guacamole datasource not found.'),
    },
)
async def get_guacamole_source(
    guac_id: GuacamoleInstance,
    guac_service: GuacamoleServiceDep,
) -> GuacamoleSchema:
    """
    **User**
    Retrieve a specific Guacamole datasource by its UUID.
    """
    model = await guac_service.read_by_id(guac_id)
    return guac_service.serialize(model)


@guac_router.patch(
    '/{guac_id}',
    response_model=GuacamoleSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Datasource not found.'),
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    },
)
async def update_guacamole_source(
    guac_id: GuacamoleInstance,
    guac_data: Annotated[CreateGuacamoleBody, Body(...)],
    guac_service: GuacamoleServiceDep,
) -> GuacamoleSchema:
    """
    **Admin**
    Update an existing Guacamole datasource.
    """
    model = await guac_service.patch_source(guac_id, guac_data)
    return guac_service.serialize(model)


@guac_router.delete(
    '/{guac_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Guacamole datasource not found.'),
    },
)
async def delete_guacamole_source(
    guac_id: GuacamoleInstance,
    guac_service: GuacamoleServiceDep,
) -> None:
    """
    Delete a Guacamole datasource by its UUID.
    """
    await guac_service.delete_source(guac_id)


@guac_router.get(
    '/connected/',
    response_model=GuacamoleSchema,
    dependencies=[Depends(UserRequired)],
    responses={
        status.HTTP_400_BAD_REQUEST: Error(
            'No Guacamole datasource is currently connected.'
        ),
        status.HTTP_404_NOT_FOUND: Error(
            'No Guacamole datasource is currently enabled.'
        ),
    },
)
async def get_connected_guacamole_source(
    guac_service: GuacamoleServiceDep,
) -> GuacamoleSchema:
    """
    Retrieve the currently enabled Guacamole datasource.
    """
    model = await guac_service.read_connected()
    return guac_service.serialize(model)


@guac_router.get(
    '/test/{datasource_id}',
    response_class=MsgspecJsonResponse,
    dependencies=[Depends(AdminRequired)],
)
async def test_guacamole_connection(
    datasource_id: GuacamoleInstance,
    guac_service: GuacamoleServiceDep,
) -> MsgspecJsonResponse:
    """
    Test the connection to a specific Guacamole datasource by its UUID.
    """
    result = await guac_service.test_connection(datasource_id)
    return MsgspecJsonResponse(content=result, status_code=status.HTTP_200_OK)


@guac_router.post(
    '/connect/{datasource_id}',
    response_model=GuacamoleSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Guacamole datasource not found.'),
        status.HTTP_400_BAD_REQUEST: Error(
            'Another datasource is already connected. Disconnect it first.'
        ),
        status.HTTP_409_CONFLICT: Error(
            'The datasource configuration is invalid, making it unreachable.'
        ),
    },
)
async def connect_guacamole_source(
    datasource_id: GuacamoleInstance,
    guac_service: GuacamoleServiceDep,
) -> GuacamoleSchema:
    """
    Connect to a specific Guacamole datasource by its UUID.
    """
    model = await guac_service.connect_by_id(datasource_id)
    return guac_service.serialize(model)


@guac_router.delete(
    '/disconnect/',
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def disconnect_guacamole(
    guac_service: GuacamoleServiceDep,
) -> None:
    """
    Disconnect the currently enabled Guacamole datasource.
    """
    await guac_service.disconnect()
