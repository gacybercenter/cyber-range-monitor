import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from range_monitor.auth.depends import AdminRequired, UserRequired
from range_monitor.schema.params import PageParamsDep
from range_monitor.sources.depends import OpenstackServiceDep
from range_monitor.sources.schemas import (
    CreateOpenstackBody,
    OpenstackPage,
    OpenstackSchema,
)
from range_monitor.utils.openapi_extra import Error
from range_monitor.utils.response_class import MsgspecJsonResponse

openstack_router = APIRouter()

OpenstackInstance = Annotated[
    uuid.UUID,
    Path(
        ...,
        description='The UUID of the Openstack instance',
    )
]

SourceLabel = Annotated[
    str,
    Query(description='Filter datasources by label')
]


@openstack_router.get(
    '/',
    response_model=OpenstackPage,
    dependencies=[Depends(UserRequired)],
)
async def list_openstack_sources(
    openstack_service: OpenstackServiceDep,
    page: PageParamsDep,
    label: SourceLabel | None = None,
) -> OpenstackPage:
    '''
    Retrieve a paginated list of Openstack datasources.
    '''
    return await openstack_service.list_datasources(label, page)


@openstack_router.post(
    '/',
    response_model=OpenstackSchema,
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    }
)
async def create_openstack_source(
    body: Annotated[CreateOpenstackBody, Body(...)],
    openstack_service: OpenstackServiceDep,
) -> OpenstackSchema:
    '''
    Create a new Openstack datasource.
    '''
    model = await openstack_service.create_source(body)
    return openstack_service.serialize(model)


@openstack_router.get(
    '/{openstack_id}',
    response_model=OpenstackSchema,
    dependencies=[Depends(UserRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Openstack datasource not found.'),
    }
)
async def get_openstack_source(
    openstack_id: OpenstackInstance,
    openstack_service: OpenstackServiceDep,
) -> OpenstackSchema:
    '''
    **User**
    Retrieve a specific Openstack datasource by its UUID.
    '''
    model = await openstack_service.read_by_id(openstack_id)
    return openstack_service.serialize(model)


@openstack_router.patch(
    '/{openstack_id}',
    response_model=OpenstackSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Datasource not found.'),
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    }
)
async def update_openstack_source(
    openstack_id: OpenstackInstance,
    body: Annotated[CreateOpenstackBody, Body(...)],
    openstack_service: OpenstackServiceDep,
) -> OpenstackSchema:
    '''
    **Admin**
    Update an existing Openstack datasource.
    '''
    model = await openstack_service.patch_source(openstack_id, body)
    return openstack_service.serialize(model)


@openstack_router.delete(
    '/{openstack_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Openstack datasource not found.'),
    }
)
async def delete_openstack_source(
    openstack_id: OpenstackInstance,
    openstack_service: OpenstackServiceDep,
) -> None:
    '''
    Delete a Openstack datasource by its UUID.
    '''
    await openstack_service.delete_source(openstack_id)


@openstack_router.get(
    '/connected/',
    response_model=OpenstackSchema,
    dependencies=[Depends(UserRequired)],
    responses={
        status.HTTP_400_BAD_REQUEST: Error(
            'No Openstack datasource is currently connected.'
        ),
        status.HTTP_404_NOT_FOUND: Error(
            'No Openstack datasource is currently enabled.'
        ),
    }
)
async def get_connected_openstack_source(
    openstack_service: OpenstackServiceDep,
) -> OpenstackSchema:
    '''
    Retrieve the currently enabled Openstack datasource.
    '''
    model = await openstack_service.read_connected()
    return openstack_service.serialize(model)


@openstack_router.get(
    '/test/{datasource_id}',
    response_class=MsgspecJsonResponse,
    dependencies=[Depends(AdminRequired)],
)
async def test_openstack_connection(
    datasource_id: OpenstackInstance,
    openstack_service: OpenstackServiceDep,
) -> MsgspecJsonResponse:
    '''
    Test the connection to a specific Openstack datasource by its UUID.
    '''
    result = await openstack_service.test_connection(datasource_id)
    return MsgspecJsonResponse(
        content=result,
        status_code=status.HTTP_200_OK
    )


@openstack_router.post(
    '/connect/{datasource_id}',
    response_model=OpenstackSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Openstack datasource not found.'),
        status.HTTP_400_BAD_REQUEST: Error(
            'Another datasource is already connected. Disconnect it first.'
        ),
        status.HTTP_409_CONFLICT: Error(
            'The datasource configuration is invalid, making it unreachable.'
        ),
    }
)
async def connect_openstack_datasource(
    datasource_id: OpenstackInstance,
    openstack_service: OpenstackServiceDep,
) -> OpenstackSchema:
    '''
    Connect to a specific Openstack datasource by its UUID.
    '''
    model = await openstack_service.connect_by_id(datasource_id)
    return openstack_service.serialize(model)


@openstack_router.delete(
    '/disconnect/',
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def disconnect_openstack_datasource(
    openstack_service: OpenstackServiceDep,
) -> None:
    '''
    Disconnect the currently enabled Openstack datasource.
    '''
    await openstack_service.disconnect()
