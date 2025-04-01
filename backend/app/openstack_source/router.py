
from typing import Annotated
from fastapi import APIRouter, Body, Security, status

from app.core.types import PathID

from app.extensions.datasources.const import NOT_ENABLED_RESPONSE, TOGGLE_ERROR_RESPONSE

from app.extensions.openapi_extra import (
    APITags, 
    ROLE_REQUIRED_DEP_RESPONSE,
    err_response_doc,
    NOT_FOUND_404
)

from app.users.dependency import (
    AdminRequired, RoleRequired, UserRequired
)

from app.core.schemas import GenericAPIResponse

from .dependency import OpenstackControllerDep
from .schema import (
    OpenstackConnectionResults,
    OpenstackCreateForm,
    OpenstackRead,
    OpenstackListResponse,
    OpenstackProtectedRead
)


openstack_router = APIRouter(
    prefix='/openstack',
    tags=[APITags.openstack_source],
    dependencies=[Security(RoleRequired)],
    responses=ROLE_REQUIRED_DEP_RESPONSE
)


@openstack_router.post(
    '/',
    response_model=OpenstackRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(AdminRequired)],
    responses={
        status.HTTP_400_BAD_REQUEST: err_response_doc('When missing both project name and ID'),
    }
)
async def create_datasource(
    openstack_data: Annotated[OpenstackCreateForm, Body(...)],
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


@openstack_router.get('/', response_model=OpenstackListResponse, responses=NOT_FOUND_404)
async def get_all_datasources(openstack_controller: OpenstackControllerDep) -> OpenstackListResponse:
    ''''Reads all the openstack datasources
    Arguments:
        openstack_controller {OpenstackControllerDep} -- the controller dependency
    Returns:
        OpenstackListResponse -- the list of openstack datasources
    '''
    return await openstack_controller.get_all_sources()


@openstack_router.get(
    '/{source_id}/details',
    response_model=OpenstackProtectedRead,
    dependencies=[Security(AdminRequired)],
    responses=NOT_FOUND_404
)
async def get_details(
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


@openstack_router.post(
    '/toggle/{source_id}',
    response_model=OpenstackRead,
    dependencies=[Security(AdminRequired)],
    responses=TOGGLE_ERROR_RESPONSE
)
async def toggle_datasource(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> OpenstackRead:
    '''toggles the enabled datasource given it's ID, a datasource that is already enabled 
    cannot be disabled. When a disabled datasource is toggled, it will be enabled and the 
    previously enabled datasource will be disabled

    Arguments:
        source_id {PathID} -- the ID of the openstack datasource to toggle
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        OpenstackRead -- the updated openstack datasource
    '''
    openstack_source = await openstack_controller.toggle_by_id(source_id)
    return OpenstackRead.to_model(openstack_source)


@openstack_router.get(
    '/test',
    response_model=OpenstackConnectionResults,
    dependencies=[Security(UserRequired)],
    responses=NOT_ENABLED_RESPONSE
)
async def test_connection(
    openstack_controller: OpenstackControllerDep
) -> OpenstackConnectionResults:
    '''Tests the connection to the openstack datasource

    Arguments:
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        GenericAPIResponse -- the api response with the details on the connection attempt
    '''
    result, err = await openstack_controller.test_enabled_source_connection()
    return OpenstackConnectionResults.create(result, err)


@openstack_router.get(
    '/test/{source_id}',
    response_model=OpenstackConnectionResults,
    dependencies=[Security(UserRequired)],
    responses=NOT_FOUND_404
)
async def test_datasource_connection(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> OpenstackConnectionResults:
    '''Tests the connection to the openstack datasource by ID 

    Arguments:
        source_id {PathID} -- the ID of the datasource
        openstack_controller {OpenstackControllerDep} -- the controller dependency

    Returns:
        GenericAPIResponse -- the api response with the details on the connection attempt
    '''
    source = await openstack_controller.get_by_id(source_id)
    result, err = await openstack_controller.test_connection(source)
    return OpenstackConnectionResults.create(result, err)


@openstack_router.get(
    '/{source_id}',
    response_model=OpenstackRead,
    dependencies=[Security(UserRequired)],
    responses=NOT_FOUND_404
)
async def get_datasource(
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
    dependencies=[Security(AdminRequired)]
)
async def update_datasource(
    source_id: PathID,
    openstack_data: Annotated[OpenstackCreateForm, Body()],
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
    dependencies=[Security(AdminRequired)],
    responses=NOT_FOUND_404
)
async def delete_datasource(
    source_id: PathID,
    openstack_controller: OpenstackControllerDep
) -> GenericAPIResponse:
    await openstack_controller.delete_by_id(source_id)
    return GenericAPIResponse(
        message='Openstack source deleted successfully',
        data={'id': source_id}
    )
