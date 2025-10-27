import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from server.app.data_sources.depends import SaltstackServiceDep
from server.app.data_sources.schemas import (
    CreateSaltstackBody,
    SaltstackPage,
    SaltstackSchema,
)
from server.app.openapi_extra import Error
from server.app.users.depends import AuthorizedAdmin, AuthorizedUser
from server.response import MsgspecJsonResponse
from server.utils.paginate import PageParamsDep

saltstack_router = APIRouter()

SaltstackInstance = Annotated[
    uuid.UUID,
    Path(
        ...,
        description='The UUID of the Saltstack instance',
    ),
]

SourceLabel = Annotated[str, Query(description='Filter datasources by label')]


@saltstack_router.get(
    '/',
    dependencies=[Depends(AuthorizedUser)],
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
    dependencies=[Depends(AuthorizedAdmin)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    },
)
async def create_saltstack_source(
    body: Annotated[CreateSaltstackBody, Body(...)],
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    Create a new Saltstack datasource.
    '''
    model = await saltstack_service.create_data_source(body)
    return saltstack_service.serialize(model)


@saltstack_router.get(
    '/{saltstack_id}',
    dependencies=[Depends(AuthorizedUser)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Saltstack datasource not found.'),
    },
)
async def get_saltstack_source(
    saltstack_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    **User**
    Retrieve a specific Saltstack datasource by its UUID.
    '''
    model = await saltstack_service.get_by_id(saltstack_id)
    return saltstack_service.serialize(model)


@saltstack_router.patch(
    '/{saltstack_id}',
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AuthorizedAdmin)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Datasource not found.'),
        status.HTTP_409_CONFLICT: Error('The label is already in use.'),
    },
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
    model = await saltstack_service.update_data_source(saltstack_id, body)
    return saltstack_service.serialize(model)


@saltstack_router.delete(
    '/{saltstack_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AuthorizedAdmin)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Saltstack datasource not found.'),
    },
)
async def delete_saltstack_source(
    saltstack_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> None:
    '''
    Delete a Saltstack datasource by its UUID.
    '''
    await saltstack_service.delete_data_source(saltstack_id)


@saltstack_router.get(
    '/connected/',
    dependencies=[Depends(AuthorizedUser)],
    responses={
        status.HTTP_400_BAD_REQUEST: Error(
            'No Saltstack datasource is currently connected.'
        ),
        status.HTTP_404_NOT_FOUND: Error('No Saltstack datasource is currently enabled.'),
    },
)
async def get_connected_saltstack_source(
    saltstack_service: SaltstackServiceDep,
) -> SaltstackSchema:
    '''
    Retrieve the currently enabled Saltstack datasource.
    '''
    model = await saltstack_service.get_connected_source()
    return saltstack_service.serialize(model)


@saltstack_router.get(
    '/test/{datasource_id}',
    response_class=MsgspecJsonResponse,
    dependencies=[Depends(AuthorizedAdmin)],
)
async def test_saltstack_connection(
    datasource_id: SaltstackInstance,
    saltstack_service: SaltstackServiceDep,
) -> MsgspecJsonResponse:
    '''
    Test the connection to a specific Saltstack datasource by its UUID.
    '''
    result = await saltstack_service.test_connection(datasource_id)
    return MsgspecJsonResponse(content=result, status_code=status.HTTP_200_OK)


@saltstack_router.post(
    '/connect/{datasource_id}',
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AuthorizedAdmin)],
    responses={
        status.HTTP_404_NOT_FOUND: Error('Saltstack datasource not found.'),
        status.HTTP_400_BAD_REQUEST: Error(
            'Another datasource is already connected. Disconnect it first.'
        ),
        status.HTTP_409_CONFLICT: Error(
            'The datasource configuration is invalid, making it unreachable.'
        ),
    },
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
    dependencies=[Depends(AuthorizedAdmin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def disconnect_saltstack_datasource(
    saltstack_service: SaltstackServiceDep,
) -> None:
    '''
    Disconnect the currently enabled Saltstack datasource.
    '''
    await saltstack_service.disconnect_data_source()
