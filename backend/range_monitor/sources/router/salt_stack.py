import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from range_monitor.auth.depends import AdminRequired, UserRequired
from range_monitor.schema.params import PageParamsDep
from range_monitor.sources.depends import SaltstackServiceDep
from range_monitor.sources.schemas import (
    CreateSaltstackBody,
    SaltstackPage,
    SaltstackSchema,
)
from range_monitor.utils.openapi_extra import Error
from range_monitor.utils.response_class import MsgspecJsonResponse

saltstack_router = APIRouter()

SaltstackInstance = Annotated[
    uuid.UUID,
    Path(
        ...,
        description='The UUID of the Saltstack instance',
    )
]

SourceLabel = Annotated[
    str,
    Query(description='Filter datasources by label')
]


@saltstack_router.get(
    '/',
    response_model=SaltstackPage,
    dependencies=[Depends(UserRequired)],
)
async def list_saltstack_sources(
    saltstack_service: SaltstackServiceDep,
    page: PageParamsDep,
    label: SourceLabel | None = None,
) -> SaltstackPage:
    '''
    Retrieve a paginated list of Saltstack datasources.
    '''
    return await saltstack_service.list_datasources(label, page)


@saltstack_router.post(
    '/',
    response_model=SaltstackSchema,
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    }
)
async def create_saltstack_source(
    body: Annotated[CreateSaltstackBody, Body(...)],
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    Create a new Saltstack datasource.
    '''
    model = await saltstack_service.create_source(body)
    return saltstack_service.serialize(model)


@saltstack_router.get(
    '/{saltstack_id}',
    response_model=SaltstackSchema,
    dependencies=[Depends(UserRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Saltstack datasource not found.'),
    }
)
async def get_saltstack_source(
    saltstack_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    **User**
    Retrieve a specific Saltstack datasource by its UUID.
    '''
    model = await saltstack_service.read_by_id(saltstack_id)
    return saltstack_service.serialize(model)


@saltstack_router.patch(
    '/{saltstack_id}',
    response_model=SaltstackSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Datasource not found.'),
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    }
)
async def update_saltstack_source(
    saltstack_id: SaltstackInstance,
    body: Annotated[CreateSaltstackBody, Body(...)],
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    **Admin**
    Update an existing Saltstack datasource.
    '''
    model = await saltstack_service.patch_source(saltstack_id, body)
    return saltstack_service.serialize(model)


@saltstack_router.delete(
    '/{saltstack_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Saltstack datasource not found.'),
    }
)
async def delete_saltstack_source(
    saltstack_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> None:
    '''
    Delete a Saltstack datasource by its UUID.
    '''
    await saltstack_service.delete_source(saltstack_id)


@saltstack_router.get(
    '/connected/',
    response_model=SaltstackSchema,
    dependencies=[Depends(UserRequired)],
    responses={
        status.HTTP_400_BAD_REQUEST: Error(
            'No Saltstack datasource is currently connected.'
        ),
        status.HTTP_404_NOT_FOUND: Error(
            'No Saltstack datasource is currently enabled.'
        ),
    }
)
async def get_connected_saltstack_source(
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    Retrieve the currently enabled Saltstack datasource.
    '''
    model = await saltstack_service.read_connected()
    return saltstack_service.serialize(model)


@saltstack_router.get(
    '/test/{datasource_id}',
    response_class=MsgspecJsonResponse,
    dependencies=[Depends(AdminRequired)],
)
async def test_saltstack_connection(
    datasource_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> MsgspecJsonResponse:
    '''
    Test the connection to a specific Saltstack datasource by its UUID.
    '''
    result = await saltstack_service.test_connection(datasource_id)
    return MsgspecJsonResponse(
        content=result,
        status_code=status.HTTP_200_OK
    )


@saltstack_router.post(
    '/connect/{datasource_id}',
    response_model=SaltstackSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Saltstack datasource not found.'),
        status.HTTP_400_BAD_REQUEST: Error(
            'Another datasource is already connected. Disconnect it first.'
        ),
        status.HTTP_409_CONFLICT: Error(
            'The datasource configuration is invalid, making it unreachable.'
        ),
    }
)
async def connect_saltstack_datasource(
    datasource_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    Connect to a specific Saltstack datasource by its UUID.
    '''
    model = await saltstack_service.connect_by_id(datasource_id)
    return saltstack_service.serialize(model)


@saltstack_router.delete(
    '/disconnect/',
    dependencies=[Depends(AdminRequired)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def disconnect_saltstack_datasource(
    saltstack_service: SaltstackServiceDep,
) -> None:
    '''
    Disconnect the currently enabled Saltstack datasource.
    '''
    await saltstack_service.disconnect()
