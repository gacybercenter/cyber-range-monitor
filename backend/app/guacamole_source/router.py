from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, Security, status

from app.core.schemas import GenericAPIResponse
from app.core.types import PathID

from app.extensions.openapi_extra import APITags

from app.users.dependency import (
    RoleRequired,
    AdminRequired,
    UserRequired
)


from .dependency import GuacControllerDep
from .schema import (
    GuacamoleCreateForm,
    GuacamoleListResponse,
    GuacamoleProtectedRead,
    GuacamoleRead,
    GuacamoleUpdateForm
)


guac_router = APIRouter(
    prefix='/guacamole',
    tags=[APITags.guac_source],
    dependencies=[Security(RoleRequired)]
)


@guac_router.post(
    '/',
    response_model=GuacamoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(AdminRequired)]
)
async def create_guacamole_datasource(
    guac_create_data: Annotated[GuacamoleCreateForm, Body(...)],
    guac_controller: GuacControllerDep
) -> GuacamoleRead:
    '''Given a form with the data to create a Guacamole datasource and an admin
    user with the proper permissions, creates a new Guacamole datasource.

    Arguments:
        guac_create_data {Annotated[GuacamoleCreateForm, Form} -- the form with the data to create a Guacamole datasource
        guac_controller {GuacControllerDep} -- the controller to use to create the Guacamole datasource

    Returns:
        GuacamoleRead -- the resulting the datasource
    '''
    obj_in = guac_create_data.serialize()
    guac_source = await guac_controller.create_datasource(obj_in)
    return GuacamoleRead.to_model(guac_source)


@guac_router.get('/', response_model=GuacamoleListResponse)
async def get_all_guacamole_sources(guac_controller: GuacControllerDep) -> GuacamoleListResponse:
    '''returns a list of all the Guacamole datasources in the system
    Arguments:
        guac_controller {GuacControllerDep} -- the controller 

    Returns:
        GuacamoleListResponse -- the response model
    '''
    return await guac_controller.get_all_sources()


@guac_router.get(
    '/details/{source_id}',
    response_model=GuacamoleProtectedRead,
    dependencies=[Security(AdminRequired)]
)
async def get_guacamole_details(
    source_id: PathID,
    guac_controller: GuacControllerDep
) -> GuacamoleProtectedRead:
    '''allows the reader to see the password field for the datasource

    Arguments:
        source_id {PathID} -- the ID of the datasource to read
        guac_controller {GuacControllerDep} -- the controller dependency

    Returns:
        GuacamoleProtectedRead -- the complete datasource model
    '''
    guac_source = await guac_controller.get_by_id(source_id)
    return GuacamoleProtectedRead.to_model(guac_source)


@guac_router.post(
    '/toggle/{source_id}/',
    response_model=GuacamoleRead,
    dependencies=[Security(AdminRequired)]
)
async def toggle_guacamole_datasource(source_id: PathID, guac_controller: GuacControllerDep) -> GuacamoleRead:
    '''given an ID of a Guacamole datasource, toggles the enabled datasource if possible

    Arguments:
        source_id {int} -- ID of the datasource to toggle
        guac_controller {GuacControllerDep} -- the controller dependency

    Returns:
        GuacamoleRead -- the resulting datasource model
    '''
    guac_source = await guac_controller.toggle_by_id(source_id)
    return GuacamoleRead.to_model(guac_source)


@guac_router.get('/test', response_model=GenericAPIResponse)
async def test_guacamole_connection(guac_controller: GuacControllerDep) -> GenericAPIResponse:
    '''tests the connection to the Guacamole datasource and returns a message
    to the user if the connection was successful or not

    Arguments:
        guac_controller {GuacControllerDep} -- the controller dependency

    Returns:
        GenericAPIResponse -- the API response model with a message and the result of the connection test
    '''
    result = await guac_controller.connect_enabled()
    if result:
        message = 'Successfully connected to the Guacamole datasource'
    else:
        message = (
            'Failed to connect to the Guacamole datasource likely '
            'due to improper credentials or a misconfiguration, please try again.'
        )
    return GenericAPIResponse(
        message=message,
        data={'result': result}
    )


@guac_router.get(
    '/test/{source_id}',
    response_model=GenericAPIResponse,
    dependencies=[Security(UserRequired)]
)
async def test_guacamole_datasource(
    source_id: PathID,
    guac_controller: GuacControllerDep
) -> GenericAPIResponse:
    '''attempts to create a session to the Guacamole datasource and whether the 
    connection was successful or not, returns a message to the user
    Arguments:
        source_id {PathID} -- the ID of the Guacamole datasource to test
        guac_controller {GuacControllerDep} -- the controller dependency
    Returns:
        GenericAPIResponse -- the API response model with a message and the result of the connection test
    '''
    test_result = await guac_controller.test_connection(source_id)
    if test_result:
        message = 'Successfully connected to the Guacamole datasource'
    else:
        message = (
            'Failed to connect to the Guacamole datasource likely '
            'due to improper credentials or a misconfiguration, please try again.'
        )
    return GenericAPIResponse(
        message=message,
        data={'id': source_id, 'result': test_result}
    )


@guac_router.get(
    '/{source_id}/',
    response_model=GuacamoleRead,
    dependencies=[Security(UserRequired)]
)
async def read_guacamole_source(source_id: PathID, guac_controller: GuacControllerDep) -> GuacamoleRead:
    '''returns the Guacamole datasource model by its ID, excluding the password field

    Arguments:
        source_id {PathID} -- the ID of the datasource to read
        guac_controller {GuacControllerDep} -- the controller dependency

    Returns:
        GuacamoleRead -- the resulting datasource model
    '''
    guac_source = await guac_controller.get_by_id(source_id)
    return GuacamoleRead.to_model(guac_source)


@guac_router.patch(
    '/{source_id}/',
    response_model=GuacamoleRead,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Security(AdminRequired)]
)
async def update_guacamole_source(
    source_id: PathID,
    guac_update_data: Annotated[GuacamoleUpdateForm, Body()],
    guac_controller: GuacControllerDep
) -> GuacamoleRead:
    '''updates a Guacamole datasource by its ID

    Arguments:
        source_id {PathID} -- the ID of the datasource to update
        guac_update_data {Annotated[GuacamoleUpdateForm, Form} -- the form with the data to update the Guacamole 
        datasource.
        guac_controller {GuacControllerDep} -- the controller dependency

    Returns:
        GuacamoleRead -- the model updated 
    '''
    guac_source = await guac_controller.update_by_id(
        source_id,
        guac_update_data.serialize()
    )
    return GuacamoleRead.to_model(guac_source)


@guac_router.delete(
    '/{source_id}/',
    response_model=GenericAPIResponse,
    dependencies=[Security(AdminRequired)]
)
async def delete_guacamole_source(
    source_id: PathID,
    guac_controller: GuacControllerDep,
) -> GenericAPIResponse:
    '''deletes a Guacamole datasource by its ID

    Arguments:
        source_id {PathID} -- the ID of the datasource to delete
        guac_controller {GuacControllerDep} -- the controller dependency

    Returns:
        GenericAPIResponse -- the API response model with a message and the ID of the deleted datasource
    '''
    await guac_controller.delete_by_id(source_id)
    return GenericAPIResponse(
        message=f"Guacamole source deleted",
        data={'id': source_id}
    )
