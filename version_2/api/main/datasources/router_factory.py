from typing import TypeVar, Generic, Type, List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


from api.utils.dependencies import needs_db
from api.main.datasources.services import DatasourceService
from api.models.mixins import DatasourceMixin
from api.utils.errors import ResourceNotFound

ReadSchemaT = TypeVar("ReadSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)


'''
for each of the datasources

/<datasource_name> [GET] - list all data sources
/<datasource_name> [POST] - create a new data source

/<datasource_name>/<datasource_id> [GET] - get a data source
/<datasource_name>/<datasource_id> [PUT] - update a data source
/<datasource_name>/<datasource_id> [DELETE] - delete a data source

/<datasource_name>/<datasource_id>/ [POST] - toggle a datasource 


but they each have different names and attributes 

'''


def create_data_source_router(
    datasource_model: Type[DatasourceMixin],
    create_schema: Type[CreateSchemaT],
    read_schema: Type[ReadSchemaT],
    update_schema: Type[UpdateSchemaT],
    datasource_name: str
) -> APIRouter:
    '''
    Creates a router and it's routes for a data source given it's pydantic schemas
    model and name datasource_name 

    Arguments:
        datasource_model {Type[DatasourceMixin]} -- the DatasourceModel
        create_schema {Type[CreateSchemaT]} -- The create schema for the datasource
        read_schema {Type[ReadSchemaT]} -- The response schema for the datasource
        update_schema {Type[UpdateSchemaT]} -- The update schema for the datasource
        datasource_name {str} -- the prefix for the datasource (e.g 'guac' > /guac)

    Returns:
        APIRouter -- the APIrouter for the Datasource
    '''

    ds_router = APIRouter(
        prefix=f'/{datasource_name}',
        tags=[f'{datasource_name.capitalize()} Datasources']
    )
    service = DatasourceService(datasource_model)

    # /<datasource_name> [GET] - list all data sources
    @ds_router.get('/', response_model=List[read_schema], status_code=status.HTTP_200_OK)
    async def get_all_datasources(db: needs_db) -> List[read_schema]:
        datasources = await service.get_all(db)
        if not datasources or len(datasources) == 0:
            raise ResourceNotFound('Datasources')
        return datasources  # type: ignore

    # /<datasource_name> [POST] - create a new data source
    @ds_router.post('/', response_model=read_schema, status_code=status.HTTP_201_CREATED)
    async def create_datasource(
        create_ds_schema: create_schema,
        db: needs_db
    ) -> read_schema:
        datasource_in = create_ds_schema.model_dump(exclude_unset=True)
        return await service.create(db, datasource_in)  # type: ignore

    # /<datasource_name>/<datasource_id> [GET] - get a data source

    @ds_router.get('/{datasource_id}', response_model=read_schema, status_code=status.HTTP_200_OK)
    async def get_datasource(datasource_id: int, db: needs_db) -> read_schema:
        datasource = await service.get_by(
            service.model.id == datasource_id,
            db
        )
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Datasource not found'
            )
        return datasource  # type: ignore

    # /<datasource_name>/<datasource_id> [PUT] - update a data source
    @ds_router.put('/{datasource_id}', response_model=read_schema, status_code=status.HTTP_200_OK)
    async def update_datasource(
        datasource_id: int,
        update_ds_schema: update_schema,
        db: needs_db,
    ) -> read_schema:
        updated_ds = await service.get_by(
            service.model.id == datasource_id,
            db
        )
        if not updated_ds:
            raise ResourceNotFound('Datasource')

        datasource_in = update_ds_schema.model_dump(exclude_unset=True)
        res = await service.update(db, updated_ds, datasource_in)
        return res  # type: ignore

    @ds_router.delete('/{datasource_id}', status_code=status.HTTP_204_NO_CONTENT)
    async def delete_datasource(datasource_id: int, db: needs_db) -> None:
        datasource = await service.get_by(
            service.model.id == datasource_id,
            db
        )
        if not datasource:
            raise ResourceNotFound('Datasource')
        await service.delete_model(db, datasource)

    # /<datasource_name>/<datasource_id>/ [POST] - toggle a datasource
    @ds_router.post('/{datasource_id}', status_code=status.HTTP_200_OK)
    async def toggle_datasource(datasource_id: int, db: needs_db) -> dict:
        success, error = await service.enable_datasource(db, datasource_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        return {'message': 'Datasource enabled'}

    return ds_router
