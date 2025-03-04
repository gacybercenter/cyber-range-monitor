from typing import Annotated, TypeVar

from fastapi import APIRouter, Body, Depends, Form, status
from pydantic import BaseModel, ConfigDict

from app.datasources.errors import DatasourceNotFound
from app.db.dependency import DatabaseRequired
from app.models.datasource.datasource_mixin import DatasourceMixin
from app.shared.errors import HTTPNotFound
from app.shared.schemas import PathID, ResponseMessage
from app.users.dependency import AdminProtected, RoleProtected

from .service import DatasourceService

ReadSchemaT = TypeVar("ReadSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)


def datasource_router(
    datasource_model: type[DatasourceMixin],
    create_schema: type[CreateSchemaT],
    read_schema: type[ReadSchemaT],
    update_schema: type[UpdateSchemaT],
    datasource_name: str,
) -> APIRouter:
    """
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
    """

    class ProtectedRead(read_schema):
        password: str
        model_config = ConfigDict(from_attributes=True)

    ds_router = APIRouter(
        prefix=f"/{datasource_name}", tags=[f"{datasource_name.capitalize()} Datasources"]
    )
    ds_service = DatasourceService(datasource_model)

    @ds_router.get(
        "/", response_model=list[read_schema], dependencies=[Depends(RoleProtected)]
    )
    async def get_all_datasources(db: DatabaseRequired) -> list[read_schema]:  # type: ignore
        """gets all of the given datasource in the database

        Arguments:
            db {DatabaseRequired} -- the database session

        Raises:
            HTTPNotFound: if no datasources are found

        Returns:
            List[read_schema] -- a list of the datasources from the database
        """

        datasources = await ds_service.get_all(db)
        if not datasources or len(datasources) == 0:
            raise DatasourceNotFound()
        return datasources  # type: ignore

    @ds_router.get(
        "/protected/{datasource_id}/",
        response_model=ProtectedRead,
        dependencies=[Depends(AdminProtected)],
    )
    async def protected_read(datasource_id: PathID, db: DatabaseRequired) -> ProtectedRead:
        datasource = await ds_service.get_by(ds_service.model.id == datasource_id, db)
        if not datasource:
            raise DatasourceNotFound()

        protected_model = ProtectedRead.model_validate(datasource, from_attributes=True)
        protected_model.password = await ds_service.get_datasource_password(datasource)
        return protected_model

    # /<datasource_name> [POST] - create a new data source
    @ds_router.post(
        "/",
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(AdminProtected)],
    )
    async def create_datasource(
        create_ds_schema: Annotated[create_schema, Form()],  # type: ignore
        db: DatabaseRequired,
    ) -> read_schema:  # type: ignore
        datasource_in = create_ds_schema.model_dump(exclude_unset=True)
        return await ds_service.create_datasource(datasource_in, db)

    @ds_router.get(
        "/{datasource_id}/",
        response_model=read_schema,
        dependencies=[Depends(RoleProtected)],
    )
    async def read_datasource(datasource_id: PathID, db: DatabaseRequired) -> read_schema:  # type: ignore
        datasource = await ds_service.get_by(ds_service.model.id == datasource_id, db)
        if not datasource:
            raise DatasourceNotFound()
        return datasource  # type: ignore

    # /<datasource_name>/<datasource_id> [PUT] - update a data source
    @ds_router.put(
        "/{datasource_id}/",
        response_model=read_schema,
        dependencies=[Depends(RoleProtected)],
    )
    async def update_datasource(
        datasource_id: PathID,
        update_ds_schema: Annotated[update_schema, Body()],  # type: ignore
        db: DatabaseRequired,
    ) -> read_schema:  # type: ignore
        """given an updated schema for a data source
        it updates the datasource in the database

        Arguments:
            datasource_id {int} -- the ID of the datasource to updated
            update_ds_schema {update_schema} -- a given datasources update schema

        Raises:
            HTTPNotFound: if the datasource is not found

        Returns:
            read_schema -- a pydantic repr of the updated datasource
        """
        updated_ds = await ds_service.get_by(ds_service.model.id == datasource_id, db)
        if not updated_ds:
            raise HTTPNotFound("Datasource")

        datasource_in = update_ds_schema.model_dump(exclude_unset=True)
        res = await ds_service.update_datasource(db, updated_ds, datasource_in)
        return res  # type: ignore

    @ds_router.delete(
        "/{datasource_id}/",
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[Depends(AdminProtected)],
    )
    async def delete_datasource(datasource_id: PathID, db: DatabaseRequired) -> None:
        """deletes a datasource given it's ID

        Arguments:
            datasource_id {int} -- the ID of the datasource to delete
            db {DatabaseRequired} -- the database session

        Raises:
            HTTPNotFound: if not found
        """
        datasource = await ds_service.get_by(ds_service.model.id == datasource_id, db)
        if not datasource:
            raise DatasourceNotFound()

        await ds_service.delete_model(db, datasource)

    # /<datasource_name>/<datasource_id>/ [POST] - toggle a datasource
    @ds_router.post(
        "/{datasource_id}/", status_code=status.HTTP_200_OK, response_model=ResponseMessage
    )
    async def toggle_datasource(
        datasource_id: PathID, db: DatabaseRequired
    ) -> ResponseMessage:
        """toggles a datasource on provided an ID. It toggles the other
        enabled datasource off

        Arguments:
            datasource_id {int} -- the ID of the datasource to enable
            db {DatabaseRequired} -- the database session

        Raises:
            DataSourceToggleError: if the datasource is already enabled
            DataSourceNotFound: if the datasource is not found
        Returns:
            ResponseMessage -- a message indicating the success of the operation
        """

        await ds_service.enable_datasource(db, datasource_id)
        return ResponseMessage(message="Datasource enabled successfully")

    return ds_router
