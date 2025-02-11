from typing import Annotated, TypeVar, Type, List
from fastapi import APIRouter, Form, HTTPException, status, Depends
from pydantic import BaseModel

from app.common.dependencies import (
    AdminRequired,
    RoleRequired,
    DatabaseRequired
)
from app.services.datasource_service import DatasourceService
from app.models.datasource.datasource_mixin import DatasourceMixin
from app.common.errors import HTTPNotFound, BadRequest
from app.common.models import ResponseMessage


ReadSchemaT = TypeVar("ReadSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)


class DatasourceRouterSchema:
    def __init__(
        self,
        datasource_model: Type[DatasourceMixin],
        create_schema: Type[CreateSchemaT],
        read_schema: Type[ReadSchemaT],
        update_schema: Type[UpdateSchemaT],
    ) -> None:
        self.datasource_model = datasource_model
        self.create_schema = create_schema
        self.read_schema = read_schema
        self.update_schema = update_schema

    def create_router(self, datasource_name: str) -> APIRouter:
        return create_data_source_router(
            self.datasource_model,
            self.create_schema,
            self.read_schema,
            self.update_schema,
            datasource_name
        )


def create_data_source_router(
    datasource_model: Type[DatasourceMixin],
    create_schema: Type[CreateSchemaT],
    read_schema: Type[ReadSchemaT],
    update_schema: Type[UpdateSchemaT],
    datasource_name: str
) -> APIRouter:
    '''
    Creates a router and it's routes for a data source given it's pydantic schemas,
    ORM model and a 'datasource_name' as the path prefix (e.g /data)

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
    ds_service = DatasourceService(datasource_model)

    # /<datasource_name> [GET] - list all data sources
    @ds_router.get(
        '/',
        response_model=List[read_schema],
        dependencies=[Depends(RoleRequired())]
    )
    # type: ignore
    async def get_all_datasources(db: DatabaseRequired) -> List[read_schema]:
        '''gets all of the given datasource in the database

        Arguments:
            db {DatabaseRequired} -- the database session

        Raises:
            HTTPNotFound: if no datasources are found

        Returns:
            List[read_schema] -- a list of the datasources from the database
        '''

        datasources = await ds_service.get_all(db)
        if not datasources or len(datasources) == 0:
            raise HTTPNotFound('Datasources')
        return datasources  # type: ignore

    # /<datasource_name> [POST] - create a new data source
    @ds_router.post(
        '/', response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(AdminRequired())]
    )
    async def create_datasource(
        create_ds_schema: Annotated[create_schema, Form()],  # type: ignore
        db: DatabaseRequired
    ) -> read_schema:  # type: ignore
        datasource_in = create_ds_schema.model_dump(exclude_unset=True)
        # type: ignore
        return await ds_service.create_datasource(db, datasource_in)

    @ds_router.get(
        '/{datasource_id}/',
        response_model=read_schema,
        dependencies=[Depends(RoleRequired())]
    )
    async def get_datasource(
        datasource_id: int,
        db: DatabaseRequired
    ) -> read_schema:  # type: ignore
        datasource = await ds_service.get_by(
            ds_service.model.id == datasource_id,
            db
        )
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Datasource not found'
            )

        return datasource  # type: ignore

    # /<datasource_name>/<datasource_id> [PUT] - update a data source
    @ds_router.put(
        '/{datasource_id}/',
        response_model=read_schema,
        dependencies=[Depends(AdminRequired())]
    )
    async def update_datasource(
        datasource_id: int,
        update_ds_schema: Annotated[update_schema, Form()],  # type: ignore
        db: DatabaseRequired,
    ) -> read_schema:  # type: ignore
        '''given an updated schema for a data source
        it updates the datasource in the database

        Arguments:
            datasource_id {int} -- the ID of the datasource to updated
            update_ds_schema {update_schema} -- a given datasources update schema

        Raises:
            HTTPNotFound: if the datasource is not found

        Returns:
            read_schema -- a pydantic repr of the updated datasource
        '''
        updated_ds = await ds_service.get_by(
            ds_service.model.id == datasource_id,
            db
        )
        if not updated_ds:
            raise HTTPNotFound('Datasource')

        datasource_in = update_ds_schema.model_dump(exclude_unset=True)
        res = await ds_service.update_datasource(db, updated_ds, datasource_in)
        return res  # type: ignore

    @ds_router.delete(
        '/{datasource_id}/',
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[Depends(AdminRequired())]
    )
    async def delete_datasource(datasource_id: int, db: DatabaseRequired) -> None:
        '''deletes a datasource given it's ID

        Arguments:
            datasource_id {int} -- the ID of the datasource to delete
            db {DatabaseRequired} -- the database session 

        Raises:
            HTTPNotFound: if not found
        '''
        datasource = await ds_service.get_by(
            ds_service.model.id == datasource_id,
            db
        )
        if not datasource:
            raise HTTPNotFound('Datasource')

        await ds_service.delete_model(db, datasource)

    # /<datasource_name>/<datasource_id>/ [POST] - toggle a datasource
    @ds_router.post('/{datasource_id}/', status_code=status.HTTP_200_OK, response_model=ResponseMessage)
    async def toggle_datasource(datasource_id: int, db: DatabaseRequired) -> ResponseMessage:
        '''toggles a datasource on provided an ID. It toggles the other 
        enabled datasource off

        Arguments:
            datasource_id {int} -- the ID of the datasource to enable
            db {DatabaseRequired} -- the database session

        Raises:
            BadRequest: if an error occurs while enabling the datasource

        Returns:
            ResponseMessage -- a message indicating the success of the operation
        '''

        success, error = await ds_service.enable_datasource(db, datasource_id)
        if not success:
            raise BadRequest(error)

        return ResponseMessage(message='Datasource enabled successfully')

    return ds_router
