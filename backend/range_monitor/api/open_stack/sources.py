

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from range_monitor.datasource.z import (
    ConnectionTestResponse,
    CreateOpenStackBody,
    OpenStackDatasource,
    OpenStackPage,
    UpdateOpenStackBody,
)
from range_monitor.open_stack.depends import OpenstackCoreServiceDep
from range_monitor.params import PageParams, TimestampParams
from range_monitor.users.depends import RoleRequired, UserRoles
from range_monitor.utils.openapi_extra import api_error

openstack_source_router = APIRouter(
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)

OpenstackID = Annotated[str, Path(
    ...,
    min_length=1,
    max_length=36,
)]

@openstack_source_router.get(
    '/',
    response_model=OpenStackPage,
)
async def list_openstack_datasources(
    page: Annotated[PageParams, Depends(PageParams.depends)],
    timestamps: Annotated[TimestampParams, Depends(TimestampParams.depends)],
    openstack_service: OpenstackCoreServiceDep,
) -> OpenStackPage:
    '''
    Lists all OpenStack datasources with pagination support.
    '''
    openstack_page = await openstack_service.paginate_datasources(
        page=page,
        timestamps=timestamps,
        dto=OpenStackDatasource
    )

    return OpenStackPage.from_results(
        data=openstack_page.items,
        total=openstack_page.total,
        page_number=page.page_number,
        page_size=page.page_size,
    )

@openstack_source_router.get(
    '/{openstack_id}/',
    response_model=OpenStackDatasource,
)
async def get_openstack_datasource_id(
    openstack_id: OpenstackID,
    openstack_service: OpenstackCoreServiceDep,
) -> OpenStackDatasource:
    '''
    Retrieves an OpenStack datasource by its ID.
    '''
    openstack_dto = await openstack_service.get_datasource(openstack_id)
    return OpenStackDatasource.convert(openstack_dto)

@openstack_source_router.delete(
    '/{openstack_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('OpenStack datasource not found')
    }
)
async def delete_openstack_datasource_id(
    openstack_id: OpenstackID,
    openstack_service: OpenstackCoreServiceDep,
) -> None:
    '''
    Deletes an OpenStack datasource by its ID.

    Parameters
    ----------
    openstack_id : OpenstackID
    openstack_service : OpenstackCoreServiceDep
    '''
    await openstack_service.delete_datasource_id(openstack_id)


@openstack_source_router.post(
    '/',
    response_model=OpenStackDatasource,
    status_code=status.HTTP_201_CREATED,
)
async def create_openstack_datasource(
    body: Annotated[CreateOpenStackBody, Body(...)],
    openstack_service: OpenstackCoreServiceDep,
) -> OpenStackDatasource:
    '''
    Creates a new OpenStack datasource.
    '''
    created = await openstack_service.create_datasource(body)
    return OpenStackDatasource.convert(created)

@openstack_source_router.patch(
    '/{datasource_id}/',
    response_model=OpenStackDatasource,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('OpenStack datasource not found'),
    }
)
async def update_openstack_datasource_id(
    datasource_id: OpenstackID,
    body: Annotated[UpdateOpenStackBody, Body(...)],
    openstack_service: OpenstackCoreServiceDep,
) -> OpenStackDatasource:
    '''
    Updates an OpenStack datasource by its ID.

    Parameters
    ----------
    datasource_id : OpenstackID
    body : CreateOpenStackBody
        _The parameters to update the datasource_
    openstack_service : OpenstackCoreServiceDep

    Returns
    -------
    OpenStackDatasource
    '''
    updated = await openstack_service.update_datasource_id(datasource_id, body)
    return OpenStackDatasource.convert(updated)


@openstack_source_router.get(
    '/test/{openstack_id}/',
    response_model=ConnectionTestResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: api_error('No enabled OpenStack datasource found'),
    }
)
async def get_connected_openstack_datasource(
    openstack_id: OpenstackID,
    openstack_service: OpenstackCoreServiceDep,
) -> ConnectionTestResponse:
    '''
    Tests the connection to the OpenStack datasource with the given ID.
    '''

    return await openstack_service.test_connection(
        openstack_id
    )

@openstack_source_router.get(
    '/enabled',
    response_model=OpenStackDatasource,
    responses={
        status.HTTP_400_BAD_REQUEST: api_error('No enabled OpenStack datasource found'),
    }
)
async def get_enabled_openstack_datasource(
    openstack_service: OpenstackCoreServiceDep,
) -> OpenStackDatasource:
    '''
    Retrieves the currently enabled OpenStack datasource.
    '''
    enabled_dto = await openstack_service.grab_enabled_datasource()
    return OpenStackDatasource.convert(enabled_dto)

@openstack_source_router.post(
    '/disable',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: api_error('No OpenStack datasource is currently enabled'),
    }
)
async def disable_openstack(
    openstack_service: OpenstackCoreServiceDep
) -> None:
    '''
    Disables any currently enabled OpenStack datasource.
    '''
    await openstack_service.disable()

@openstack_source_router.post(
    '/enable/{openstack_id}',
    response_model=OpenStackDatasource,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('OpenStack datasource not found'),
        status.HTTP_400_BAD_REQUEST: api_error('OpenStack datasource is already enabled'),
    }
)
async def enable_openstack_datasource_id(
    openstack_id: OpenstackID,
    openstack_service: OpenstackCoreServiceDep
) -> OpenStackDatasource:
    '''
    Enables a specific OpenStack datasource by its ID.
    '''
    enabled = await openstack_service.enable_by_id(openstack_id)
    return OpenStackDatasource.convert(enabled)