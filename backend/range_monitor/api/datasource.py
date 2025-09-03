
from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from range_monitor.datasource.depends import DataSourceRepoDep
from range_monitor.datasource.schema import DatasourceListResponse, DataSourceResponse
from range_monitor.datasource.types import DataSourceType
from range_monitor.params import PageParams, TimestampParams
from range_monitor.users.depends import authorization_required
from range_monitor.utils.openapi_extra import api_error

datasource_router = APIRouter(
    dependencies=[
        Depends(authorization_required)
    ]
)


DatasourceID = Annotated[str, Path(
    ...,
    description='The unique identifier of the data source',
    min_length=1,
    max_length=64,
    example='datasource-123',
)]

Sources = Annotated[DataSourceType, Path(
    ...,
    description='Type of the data source',
    example=DataSourceType.GUACAMOLE,
)]

@datasource_router.post(
    '/{datasource_type}/enable/{datasource_id}/',
    response_model=DataSourceResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: api_error(
            'Data source already enabled or invalid type '
        ),
        status.HTTP_404_NOT_FOUND: api_error('Data source not found'),
    }
)
async def enable_datasource(
    datasource_type: Sources,
    datasource_id: DatasourceID,
    datasources: DataSourceRepoDep,
) -> DataSourceResponse:
    return await datasources.enable_by_id(datasource_id, datasource_type)


@datasource_router.get('/', response_model=DatasourceListResponse)
async def list_all_datasources(
    datasources: DataSourceRepoDep,
    timestamp_params: Annotated[TimestampParams, Depends(TimestampParams.depends)],
    page_params: Annotated[PageParams, Depends(PageParams.depends)],
) -> DatasourceListResponse:
    """
    Lists all data sources with optional filtering and pagination.
    """
    return await datasources.query_datasources(
        page_params=page_params,
        timestamp_params=timestamp_params,
    )

@datasource_router.get('/{datasource_id}/', response_model=DataSourceResponse)
async def get_datasource_id(
    datasource_id: DatasourceID,
    datasources: DataSourceRepoDep,
) -> DataSourceResponse:
    """
    Retrieves a data source by its ID.
    """
    return await datasources.get_by_id(datasource_id)

@datasource_router.get('/{datasource_type}/', response_model=DatasourceListResponse)
async def list_datasource_type(
    datasource_type: Sources,
    page_params: Annotated[PageParams, Depends(PageParams.depends)],
    timestamp_params: Annotated[TimestampParams, Depends(TimestampParams.depends)],
    datasources: DataSourceRepoDep,
) -> DatasourceListResponse:
    """
    Lists data sources by their type with optional filtering and pagination.
    """
    return await datasources.query_datasources(
        of_type=datasource_type,
        page_params=page_params,
        timestamp_params=timestamp_params
    )

@datasource_router.delete(
    '/{datasource_type}/{datasource_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Data source not found'),
        status.HTTP_400_BAD_REQUEST: api_error(
            'Data source already disabled or invalid type'
        ),
    }
)
async def delete_datasource_type_id(
    datasource_type: Sources,
    datasource_id: DatasourceID,
    datasources: DataSourceRepoDep,
) -> None:
    """
    Deletes a data source by its ID and type.
    """
    await datasources.delete_by_id(datasource_id, datasource_type)

