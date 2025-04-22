
from typing import Annotated
from fastapi import APIRouter, Security, status, Path

from app.misc.openapi_extra import (
    AUTH_DEP_RESPONSES,
    APITags,
    NOT_FOUND_404,
    err_response_doc
)

from app.db.dependency import DatabaseDep
from app.core.types import PathID
from app.domains.users.dependency import (
    RoleRequired,
    AdminRequired,
    UserRequired
)


from app.core.schemas import APIListResponse, GenericAPIResponse

from app.misc.logging import APILogging

from .schema import (
    DatasourceDeleteData,
    DatasourceDeleteResponse,
    ConnectionTestResults
)


from .dependency import (
    DatasourceServiceDep,
    DatasourceCreateDep,
    DatasourceUpdateDep,
    DatasourceResponseSchema,
    DatasourceListResponses
)

ds_router = APIRouter(
    prefix='/datasources',
    dependencies=[Security(RoleRequired)],
    responses=AUTH_DEP_RESPONSES,
    tags=[APITags.datasource]
)


@ds_router.get(
    '/{datasource}/',
    response_model=DatasourceListResponses,
    status_code=status.HTTP_200_OK
)
async def read_all_datasources(
    service: DatasourceServiceDep
) -> DatasourceListResponses:
    """Gets all of the datasources of a given type and returns the 
    response or 404 if none exist.
    Arguments:
        datasource {DatasourcePath} -- the datasource type to act on
        db {DatabaseDep} -- the database dependency
    Returns: 
        APIListResponse[DatasourceResponse] -- the response model containing 
        the list of datasources
    """
    datasources = await service.get_all()
    return APIListResponse.from_list(datasources)  # type: ignore


@ds_router.post(
    '/{datasource}/',
    response_model=DatasourceResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: err_response_doc(
            'Options weren\'t provided.')
    },
    dependencies=[Security(AdminRequired)]
)
async def create_datasource(
    req_body: DatasourceCreateDep,
    service: DatasourceServiceDep
) -> DatasourceResponseSchema:
    """Create a new datasource of a given type"""
    datasource = await service.create_new(req_body)  # type: ignore
    return datasource


@ds_router.patch(
    '/{datasource}/update/{datasource_id}',
    response_model=DatasourceResponseSchema,
    responses=NOT_FOUND_404,
    dependencies=[Security(AdminRequired)]
)
async def update_datasource_id(
    req_body: DatasourceUpdateDep,
    service: DatasourceServiceDep,
    datasource_id: PathID
) -> DatasourceResponseSchema:
    """Update a datasource of a given type"""

    datasource = await service.update_by_id(
        req_body,  # type: ignore
        datasource_id
    )
    return datasource  # type: ignore


@ds_router.delete(
    '/{datasource}/delete/{datasource_id}',
    response_model=GenericAPIResponse,
    responses=NOT_FOUND_404,
    dependencies=[Security(AdminRequired)]
)
async def delete_datasource_id(
    service: DatasourceServiceDep,
    datasource_id: PathID
) -> DatasourceDeleteResponse:
    """Delete a datasource of a given type"""

    to_delete = await service.models.get_by_id(datasource_id)  # type: ignore

    # create before delete data before session commits
    response_meta = DatasourceDeleteData(
        id=datasource_id,
        datasource_type=service.models.model.__name__,
        username=to_delete.username,
        was_enabled=to_delete.enabled
    )

    await service.models.delete(to_delete)  # type: ignore
    return DatasourceDeleteResponse(
        success=True,
        message='Datasource deleted successfully.',
        data=response_meta
    )


@ds_router.get(
    '/{datasource}/read/{datasource_id}',
    response_model=DatasourceResponseSchema,
    responses=NOT_FOUND_404,
    dependencies=[Security(UserRequired)]
)
async def read_datasource_id(
    service: DatasourceServiceDep,
    datasource_id: PathID,
) -> DatasourceResponseSchema:
    """Get a datasource of a given type"""

    model = await service.models.get_by_id(datasource_id)
    response = service.to_response(model)  # type: ignore

    return response  # type: ignore


@ds_router.get(
    '/{datasource}/test/{datasource_id}',
    response_model=ConnectionTestResults,
    dependencies=[Security(UserRequired)],
    responses=NOT_FOUND_404
)
async def test_connection_id(
    service: DatasourceServiceDep,
    datasource_id: PathID
) -> ConnectionTestResults:
    """Test the connection of a datasource of a given type"""
    model = await service.models.get_by_id(datasource_id)

    err, success = await service.test_connection(model)  # type: ignore
    msg = 'Connection attempt '
    msg += 'failed.' if err else 'succeeded.'
    return ConnectionTestResults(
        message=msg,
        error=err,
        success=success
    )


@ds_router.post(
    '/{datasource}/toggle/{datasource_id}',
    response_model=DatasourceResponseSchema,
    responses={
        **NOT_FOUND_404,
        status.HTTP_400_BAD_REQUEST: err_response_doc(
            'Datasource toggle error.'
        ),
    },
    dependencies=[Security(UserRequired)]
)
async def toggle_datasource_id(
    service: DatasourceServiceDep,
    datasource_id: PathID,
) -> DatasourceResponseSchema:
    toggled_result = await service.toggle_by_id(datasource_id)
    response = service.to_response(toggled_result)  # type: ignore

    return response  
