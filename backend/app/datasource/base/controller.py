from typing import Any, TypeVar

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.controller import CRUDController, ModelT

from app.extensions.security import crypto


from app.core.schemas import CustomBaseModel

from .schema import (
    ConnectionTestResult, DatasourceConnectionModel, DatasourceListResponse, DatasourceReadModel
)
from .model import DatasourceMixin
from .errors import (
    DatasourceNotFound,
    DatasourceToggleError,
    InvalidDatasourceSchema,
    NoEnabledDatasourceError
)

DatasourceT = TypeVar("DatasourceT", bound="DatasourceMixin")
ConnT = TypeVar("ConnT")


class DatasourceService(CRUDController[ModelT]):
    '''Outlines the methods that a datasource service
    can implement seperated from the controller class
    for readability.

    Arguments:
        CRUDController {_type_} -- _description_
    '''
    # Optional Method(s)

    def _validate_schema(self, request_schema: CustomBaseModel) -> dict:
        '''Validates the request schema and serializes it into a dictionary
        by default, it simply serializes the schema

        Arguments:
            request_schema {CustomBaseModel} -- the request schema

        Returns:
            dict -- the serialized schema
        '''
        return request_schema.serialize()

    # NOTE: ** MUST IMPLEMENT METHODS BELOW **

    def serialize(self, source: ModelT) -> DatasourceReadModel:
        '''Serializes the datasource model into a DatasourceConnectionModel
        Arguments:
            source {ModelT} -- the datasource model

        Returns:
            DatasourceConnectionModel -- the serialized model
        '''
        raise NotImplementedError()

    async def connect_args(self, source: ModelT) -> DatasourceConnectionModel:
        '''Converts a datasource model into a Pydantic Schema 
        for which when serialized represents a dictionary of 
        the arguments to create a connection instance

        Arguments:
            source {ModelT} -- the datasource model

        Returns:
            Any -- The connection arguments
        '''
        raise NotImplementedError()

    async def connect(self, source: ModelT) -> Any:
        '''Creates a connection instance from a datasource model
        Arguments:
            source {ModelT} -- the datasource model

        Returns:
            Any -- The connection instance
        '''
        raise NotImplementedError()

    async def test_datasource_connection(self, source: ModelT) -> tuple[str | None, bool]:
        '''Tests the connection to the datasource

        Arguments:
            source {ModelT} -- the datasource model

        Returns:
            tuple[str, bool] -- the connection status
        '''
        raise NotImplementedError()


class DatasourceController(DatasourceService[ModelT]):
    """The base controller class for all datasources"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_sources(self) -> DatasourceListResponse:
        '''gets all of the datasource models in the database

        Arguments:
            db {AsyncSession} -- the database session

        Raises:
            DatasourceNotFound: if no datasources are found in the database

        Returns:
            list[DatasourceMixin] -- the list of datasources retrieved
        '''
        sources = await self.get_all(self.db)
        if not sources or len(sources) == 0:
            raise DatasourceNotFound()

        data = [self.serialize(source) for source in sources]
        return DatasourceListResponse.from_list(data)
        
        
    async def get_by_id(self, id: int) -> ModelT:
        '''gets a datasource by it's ID, raises 404 if not found

        Arguments:
            db {AsyncSession} -- the DB session
            id {int} -- the ID of the datasource

        Raises:
            DatasourceNotFound: if not found

        Returns:
            DatasourceMixin -- the ORM instance
        '''
        source = await self.get_by(self.model.id == id, self.db)  # type: ignore
        if not source:
            raise DatasourceNotFound()
        return source

    async def toggle_by_id(self, datasource_id: int) -> ModelT:
        """enables a datasource in the database; the selected datasource cannot be
        disabled

        Arguments:
            db {AsyncSession}
            datasource_id {int} id of the datasource to enable
        """
        pressed_datasource: DatasourceMixin = await self.get_by_id(datasource_id)  # type: ignore
        if pressed_datasource.enabled:
            raise DatasourceToggleError('Datasource is already enabled')

        await self.db.execute(
            update(self.model).values(enabled=False)
        )
        pressed_datasource.enabled = True
        await self.db.commit()
        await self.db.refresh(pressed_datasource)
        return pressed_datasource  # type: ignore

    async def get_enabled_source(self) -> ModelT | Any:
        """returns the enabled datasource

        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            List[DatasourceMixin] -- list of enabled datasources
        """
        return await self.get_by(self.model.enabled.is_(True), self.db)  # type: ignore

    async def require_enabled(self) -> ModelT:
        """returns the enabled datasource or raises an error if none is found

        Returns:
            DatasourceMixin -- the enabled datasource
        """
        enabled_source = await self.get_enabled_source()
        if not enabled_source:
            raise NoEnabledDatasourceError("No enabled datasource found")
        return enabled_source

    async def create_datasource(self, request_args: CustomBaseModel) -> DatasourceReadModel:
        """given a dictionary of the kwargs to create a datasource, the datasource
        is created and the password is encrypted before being saved to the database
        additionally the _validate_schema method is called to validate the schema
        which not overriden simply serializes the schema

        Arguments:
            obj_in {dict} -- the "model_dump" of the datasource
            db {AsyncSession}

        Raises:
            BadRequest: the password was not in the request

        Returns:
            DatasourceReadModel -- the created datasource
        """
        obj_in = self._validate_schema(request_args)
        if "password" not in obj_in:
            raise InvalidDatasourceSchema(
                "You must provide a password for the datasource")
        obj_in["password"] = crypto.encrypt_data(obj_in["password"])
        created_model = await self.create(self.db, obj_in)
        return self.serialize(created_model)  # type: ignore

    async def update_by_id(
        self, datasource_id: int, obj_in: dict
    ) -> DatasourceReadModel:
        """Given a datasource ORM instance and a dictionary of the kwargs to update
        the datasource, the datasource is updated and the password is encrypted before
        being saved to the database

        Arguments:
            db {AsyncSession}
            datasource {DatasourceMixin}
            obj_in {dict}

        Raises:
            BadRequest: the password was not in the request
        Returns:
            DatasourceReadModel -- the updated datasource
        """
        if 'enabled' in obj_in:
            del obj_in['enabled']
        target_datasource = await self.get_by_id(datasource_id)
        if "password" in obj_in:
            obj_in["password"] = crypto.encrypt_data(obj_in["password"])
        updated_model = await self.update(self.db, target_datasource, obj_in)
        return self.serialize(updated_model)  # type: ignore

    async def test_connection(self, source: ModelT) -> ConnectionTestResult:
        '''Tests the connection to the datasource given a it's model
        by creating a connection instance and testing the connection 

        Arguments:
            source {ModelT} -- the datasource to test

        Returns:
            ConnectionTestResult -- the connection test result
        '''
        success_msg = "Successfully connected to the datasource"
        error_msg = "Failed to connect to the datasource"
        error, success = await self.test_datasource_connection(source)
        return ConnectionTestResult(
            message=success_msg if success else error_msg,
            success=success,
            error=error
        )

    async def delete_by_id(self, datasource_id: int) -> None:
        '''Given a datasource ID, deletes the datasource from the database
        if it exists

        Arguments:
            datasource_id {int} -- the ID of the datasource to delete
        '''
        target_datasource = await self.get_by_id(datasource_id)
        await self.delete(self.db, target_datasource)  # type: ignore

    async def read_datasource_password(self, datasource_orm: DatasourceMixin) -> str:
        """Gets the decrypted password from a datasource ORM instance, only should be accesible to admins
        updating datasources or for connecting to the datasource
        Arguments:
            datasource_orm {DatasourceMixin}
        Returns:
            str -- the decrypted password
        """
        decrypted_password = crypto.decrypt_data(datasource_orm.password)
        return decrypted_password

    async def connect_enabled(self) -> Any:
        '''Creates a connection instance from the enabled datasource model
        Arguments:
            source {ModelT} -- the datasource model

        Returns:
            Any -- The connection instance
        '''
        return await self.connect(await self.require_enabled())  # type: ignore
