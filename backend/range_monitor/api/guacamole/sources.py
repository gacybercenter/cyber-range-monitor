import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, status

from range_monitor.datasource.schema import (
    ConnectionTestResponse,
    CreateGuacamoleBody,
    GuacamoleDatasource,
    GuacamolePage,
    UpdateGuacamoleBody,
)
from range_monitor.guac.depends import GuacCoreServiceDep
from range_monitor.params import PageParams, TimestampParams
from range_monitor.users.depends import RoleRequired, UserRoles
from range_monitor.utils.openapi_extra import api_error

guac_source_router = APIRouter(
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)

GuacamoleID = Annotated[str, Path(
    ...,
    min_length=1,
    max_length=36,
)]


@guac_source_router.get(
    '/',
    response_model=GuacamolePage,
)
async def list_guacamole_datasources(
    page: Annotated[PageParams, Depends(PageParams.depends)],
    timestamps: Annotated[TimestampParams, Depends(TimestampParams.depends)],
    guac_service: GuacCoreServiceDep
) -> GuacamolePage:

    guac_page = await guac_service.paginate_datasources(
        page=page,
        timestamps=timestamps,
        dto=GuacamoleDatasource
    )
    return GuacamolePage.from_results(
        data=guac_page.items,
        total=guac_page.total,
        page_number=page.page_number,
        page_size=page.page_size,
    )

@guac_source_router.get(
    '/{guac_id}/',
    response_model=GuacamoleDatasource,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Guacamole datasource not found'),
    }
)
async def get_guacamole_datasource_id(
    guac_id: GuacamoleID,
    guac_service: GuacCoreServiceDep
) -> GuacamoleDatasource:
    '''
    Retrieves a Guacamole datasource by its ID.

    Parameters
    ----------
    guac_id : GuacamoleID

    Returns
    -------
    GuacamoleDatasource
    '''
    guac = await guac_service.get_datasource(guac_id)
    return GuacamoleDatasource.convert(guac)

@guac_source_router.post(
    '/',
    response_model=GuacamoleDatasource,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)
async def create_guacamole_datasource(
    body: Annotated[CreateGuacamoleBody, Body(...)],
    guac_service: GuacCoreServiceDep
) -> GuacamoleDatasource:
    '''
    Creates a new Guacamole datasource.

    Parameters
    ----------
    guac_in : GuacamoleDatasource

    Returns
    -------
    GuacamoleDatasource
    '''
    created = await guac_service.create_datasource(body)
    return GuacamoleDatasource.convert(created)


@guac_source_router.patch(
    '/{guac_id}/',
    response_model=GuacamoleDatasource,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Guacamole datasource not found'),
    },
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)
async def update_guacamole_datasource_id(
    guac_id: GuacamoleID,
    body: Annotated[UpdateGuacamoleBody, Body(...)],
    guac_service: GuacCoreServiceDep
) -> GuacamoleDatasource:
    '''
    Updates an existing Guacamole datasource by its ID.

    Parameters
    ----------
    guac_id : GuacamoleID
    guac_in : GuacamoleDatasource

    Returns
    -------
    GuacamoleDatasource
    '''
    updated = await guac_service.update_datasource_id(guac_id, body)
    return GuacamoleDatasource.convert(updated)

@guac_source_router.delete(
    '/{guac_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Guacamole datasource not found'),
    },
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)
async def delete_guacamole_datasource_id(
    guac_id: GuacamoleID,
    guac_service: GuacCoreServiceDep
) -> None:
    '''
    Deletes an existing Guacamole datasource by its ID.

    Parameters
    ----------
    guac_id : GuacamoleID

    Returns
    -------
    None
    '''
    await guac_service.delete_datasource_id(guac_id)



@guac_source_router.get(
    '/test/{guac_id}',
    response_model=ConnectionTestResponse,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Guacamole datasource not found'),
    }
)
async def test_guacamole_datasource_id(
    guac_id: GuacamoleID,
    bg_tasks: BackgroundTasks,
    guac_service: GuacCoreServiceDep
) -> ConnectionTestResponse:
    '''
    Tests the connection to a specific Guacamole datasource by its ID.

    Returns
    -------
    ConnectionTestResponse
    '''
    return await guac_service.test_connection(bg_tasks, guac_id)

@guac_source_router.get(
    '/connection',
    response_model=GuacamoleDatasource,
    responses={
        status.HTTP_400_BAD_REQUEST: api_error('No enabled Guacamole datasource found'),
    }
)
async def get_connected_guacamole_datasource(
    guac_service: GuacCoreServiceDep
) -> GuacamoleDatasource:
    '''
    Retrieves the currently connected Guacamole datasource.
    '''
    logging.getLogger(__name__).error('here\n\n\n')
    connected = await guac_service.grab_enabled_datasource()
    return GuacamoleDatasource.convert(connected)

@guac_source_router.post(
    '/enable/{guac_id}',
    response_model=GuacamoleDatasource,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Guacamole datasource not found'),
        status.HTTP_400_BAD_REQUEST: api_error('Guacamole datasource is already enabled'),
    },
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)
async def enable_guacamole_datasource_id(
    guac_id: GuacamoleID,
    guac_service: GuacCoreServiceDep
) -> GuacamoleDatasource:
    '''
    Enables a specific Guacamole datasource by its ID.

    '''
    enabled = await guac_service.enable_by_id(guac_id)
    return GuacamoleDatasource.convert(enabled)

@guac_source_router.post(
    '/disable/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: api_error('No Guacamole datasource is currently enabled'),
    },
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ]
)
async def disable_guacamole(
    guac_service: GuacCoreServiceDep
) -> None:
    '''
    Disables the currently enabled Guacamole datasource.

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    await guac_service.disable()