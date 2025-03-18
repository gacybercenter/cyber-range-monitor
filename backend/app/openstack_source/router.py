
from typing import Annotated
from fastapi import APIRouter, Depends, Form, status

from app.core.types import PathID

from app.extensions.openapi_extra import APITags

from app.users.dependency import (
    AdminRequired, RoleRequired, UserRequired
)

from app.core.schemas import GenericAPIResponse


from .dependency import OpenstackControllerDep
from .schema import (
    OpenstackCreateForm,
    OpenstackRead,
    OpenstackListResponse,
    OpenstackProtectedRead
)


openstack_router = APIRouter(
    prefix='/openstack',
    tags=[APITags.openstack_source],
    dependencies=[Depends(RoleRequired)]
)


@openstack_router.post(
    '/',
    response_model=OpenstackRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AdminRequired)]
)
async def create_openstack_datasource(
    openstack_data: Annotated[OpenstackCreateForm, Form(...)],
    openstack_controller: OpenstackControllerDep
) -> OpenstackRead:
    '''Creates a new openstack datasource

    Arguments:
        openstack_data {Annotated[OpenstackCreateForm, Form} -- the openstack datasource data
        openstack_controller {OpenstackControllerDep} -- the openstack controller dependency

    Returns:
        OpenstackRead -- the created openstack datasource
    '''
    obj_in = openstack_data.serialize()
    openstack_source = await openstack_controller.create_datasource(obj_in)
    return OpenstackRead.to_model(openstack_source)


@openstack_router.get('/', response_model=OpenstackListResponse)
async def read_all_openstack_sources(openstack_controller: OpenstackControllerDep) -> OpenstackListResponse:
    return await openstack_controller.get_all_sources()


@openstack_router.get(
    '/{source_id}/protected',
    response_model=OpenstackProtectedRead,
    dependencies=[Depends(AdminRequired)]
)
async def read_openstack_source_details(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> OpenstackProtectedRead:
    '''Reads the details of an openstack datasource, (i.e w/ the password)

    Arguments:
        source_id {PathID} -- the datasource id 
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        OpenstackProtectedRead -- the openstack datasource details
    '''
    openstack_source = await openstack_controller.get_by_id(source_id)
    return OpenstackProtectedRead.to_model(openstack_source)


@openstack_router.post('/toggle/{source_id}', response_model=OpenstackRead, dependencies=[Depends(AdminRequired)])
async def toggle_openstack_source(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> OpenstackRead:
    openstack_source = await openstack_controller.enable_by_id(source_id)
    return OpenstackRead.to_model(openstack_source)


@openstack_router.get(
    '/connection/status',
    response_model=GenericAPIResponse,
    dependencies=[Depends(UserRequired)]
)
async def enabled_openstack_connection_status(
    openstack_controller: OpenstackControllerDep
) -> GenericAPIResponse:
    '''Attempts to connect to the openstack datasource returning 
    the result of the connection attept

    Arguments:
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        GenericAPIResponse -- the api response with the details on the connection attempt
        and errors, if Any
    '''
    result, err = await openstack_controller.test_enabled_source_connection()
    message = 'Successfully connected to the openstack datasource'
    if not result:
        message = f'Could not connect to the openstack datasource: {err}'

    return GenericAPIResponse(
        message=message,
        data={'result': result, 'error': err}
    )


@openstack_router.get(
    '/connection/test/{source_id}',
    response_model=GenericAPIResponse,
    dependencies=[Depends(UserRequired)]
)
async def test_openstack_connection(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> GenericAPIResponse:
    '''Tests the connection to the openstack datasource by ID 

    Arguments:
        source_id {PathID} -- the ID of the datasource
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        GenericAPIResponse -- the api response with the details on the connection attempt
    '''
    result, err = await openstack_controller.test_connection(source_id)
    message = 'Successfully connected to the openstack datasource'
    if not result:
        message = f'Could not connect to the openstack datasource: {err}'

    return GenericAPIResponse(
        message=message,
        data={'result': result, 'error': err}
    )


@openstack_router.get('/{source_id}', response_model=OpenstackRead, dependencies=[Depends(UserRequired)])
async def read_openstack_source(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> OpenstackRead:
    '''Reads an openstack datasource by ID

    Arguments:
        source_id {PathID} -- The ID of the datasource
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        OpenstackRead -- the openstack datasource
    '''
    openstack_source = await openstack_controller.get_by_id(source_id)
    return OpenstackRead.to_model(openstack_source)


@openstack_router.patch(
    '/{source_id}',
    response_model=OpenstackRead,
    dependencies=[Depends(AdminRequired)]
)
async def update_openstack_source(
    source_id: PathID,
    openstack_data: Annotated[OpenstackCreateForm, Form(...)],
    openstack_controller: OpenstackControllerDep
) -> OpenstackRead:
    '''Updates an openstack datasource by ID

    Arguments:
        source_id {PathID} -- The ID of the datasource
        openstack_data {Annotated[OpenstackCreateForm, Form} -- the updated data
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        OpenstackRead -- the resulting updated datasource
    '''
    obj_in = openstack_data.serialize()
    openstack_source = await openstack_controller.update_by_id(source_id, obj_in)
    return OpenstackRead.to_model(openstack_source)


@openstack_router.delete(
    '/{source_id}',
    response_model=GenericAPIResponse,
    dependencies=[Depends(AdminRequired)]
)
async def delete_openstack_source(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> GenericAPIResponse:
    await openstack_controller.delete_by_id(source_id)
    return GenericAPIResponse(
        message='Openstack source deleted successfully',
        data={'id': source_id}
    )
