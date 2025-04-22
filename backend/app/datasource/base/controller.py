# from typing import Any, Generic, Type

# from abc import ABC

# from sqlalchemy import update
# from sqlalchemy.ext.asyncio import AsyncSession


# from app.core.security import crypto

# from app.core.schemas import APIListResponse


# from .schema import (
#     ConnectionTestResult,
#     DatasourceCreateModel
# )
# from .errors import (
#     DatasourceNotFound,
#     DatasourceToggleError,
#     InvalidDatasourceSchema,
#     NoEnabledDatasourceError
# )
# from .types import (
#     DSMixin, 
#     ReadMixin,
#     DatasourceServiceABC
# )


# class DatasourceController(DatasourceServiceABC[DSMixin, ReadMixin], Generic[DSMixin, ReadMixin]):
#     """The base service class for all datasources with the shared logic
#     and operations. Refer to the DatasourceService for the methods that must
#     be implemented by child classes.

#     Arguments:
#         - M: The Database model for the datasource (must still set self.model in constructor)
#         - R: The read model for the datasource (i.e the schema returned by the API of the model)
#     """
#     def __init__(self, db: AsyncSession) -> None:
#         self.model: Type[DSMixin] = None # type: ignore
#         self.db = db
        
#     # ==== Optional override(s) ====

#     def _validate_schema(self, request_schema: DatasourceCreateModel) -> dict:
#         '''Validates the request schema and serializes it into a dictionary
#         by default, it simply serializes the schema. This is called in the
#         create_datasource method which can be used to check the schema before
#         the model is created in the databse.

#         Arguments:
#             request_schema {CustomBaseModel} -- the request schema

#         Returns:
#             dict -- the serialized schema
#         '''
#         return request_schema.serialize()

#     # NOTE: ** must implement  **

#     def serialize(self, source: DSMixin) -> ReadMixin:
#         '''Serializes the datasource model into a DatasourceConnectionModel
#         Arguments:
#             source {DatasourceMixin} -- the datasource model

#         Returns:
#             DatasourceConnectionModel -- the serialized model
#         '''
#         raise NotImplementedError()

#     async def connect_args(self, source: DSMixin) -> DatasourceConnectionModel:
#         '''Converts a datasource model into a Pydantic Schema 
#         for which when serialized represents a dictionary of 
#         the arguments to create a connection instance

#         Arguments:
#             source {DatasourceMixin} -- the datasource model

#         Returns:
#             Any -- The connection arguments
#         '''
#         raise NotImplementedError()

#     async def connect(self, source: DSMixin) -> Any:
#         '''Creates a connection instance from a datasource model
#         Arguments:
#             source {DatasourceMixin} -- the datasource model

#         Returns:
#             Any -- The connection instance
#         '''
#         raise NotImplementedError()

#     async def test_datasource_connection(self, source: DSMixin) -> tuple[str | None, bool]:
#         '''Tests the connection to the datasource

#         Arguments:
#             source {DatasourceMixin} -- the datasource model

#         Returns:
#             tuple[str, bool] -- the connection status
#         '''
#         raise NotImplementedError()
    
#     async def get_all_sources(self) -> APIListResponse[ReadMixin]:
#         '''gets all of the datasource models in the database

#         Arguments:
#             db {AsyncSession} -- the database session

#         Raises:
#             DatasourceNotFound: if no datasources are found in the database

#         Returns:
#             list[DatasourceMixin] -- the list of datasources retrieved
#         '''
#         sources = await self.get_all(self.db)
#         if not sources or len(sources) == 0:
#             raise DatasourceNotFound()

#         data = [self.serialize(source) for source in sources]
#         return APIListResponse[ReadMixin].from_list(data)

#     def serialize_models(
#         self,
#         models: list[DSMixin]
#     ) -> APIListResponse[ReadMixin]:
#         '''serializes a list of datasource models to a list of
#         datasource read models

#         Arguments:
#             models {list[DatasourceT]} -- the list of datasource models

#         Returns:
#             DatasourceListResponse[DatasourceReadT] -- the list of serialized models
#         '''
#         data = [self.serialize(source) for source in models]
#         return APIListResponse.from_list(data)

#     async def get_by_id(self, id: int) -> DSMixin:
#         '''gets a datasource by it's ID, raises 404 if not found

#         Arguments:
#             db {AsyncSession} -- the DB session
#             id {int} -- the ID of the datasource

#         Raises:
#             DatasourceNotFound: if not found

#         Returns:
#             DatasourceMixin -- the ORM instance
#         '''
#         source = await self.get_by(self.model.id == id, self.db)
#         if not source:
#             raise DatasourceNotFound()
#         return source

#     async def enable(self, pressed_datasource: DSMixin) -> DSMixin:
#         '''Enables a datasource by setting the enabled field to True

#         Arguments:
#             pressed_datasource {DatasourceT} -- the datasource to enable

#         Raises:
#             DatasourceToggleError: if the datasource is already enabled

#         Returns:
#             DatasourceT -- the enabled datasource
#         '''
#         if pressed_datasource.enabled:
#             raise DatasourceToggleError('Datasource is enabled')

#         await self.db.execute(
#             update(self.model).values(enabled=False)
#         )
#         pressed_datasource.enabled = True
#         await self.db.commit()
#         await self.db.refresh(pressed_datasource)
#         return pressed_datasource

#     async def disable(self, pressed_datasource: DSMixin) -> DSMixin:
#         '''Disables a datasource by setting the enabled field to False

#         Arguments:
#             pressed_datasource {DatasourceT} -- the datasource to disable

#         Raises:
#             DatasourceToggleError: if the datasource is already disabled

#         Returns:
#             DatasourceT -- the disabled datasource
#         '''
#         if not pressed_datasource.enabled:
#             raise DatasourceToggleError('Datasource is disabled')

#         pressed_datasource.enabled = False
#         await self.db.commit()
#         await self.db.refresh(pressed_datasource)
#         return pressed_datasource

#     async def toggle(self, pressed_datasource: DSMixin) -> DSMixin:
#         stmnt = (
#             update(self.model)
#             .where(self.model.id != pressed_datasource.id)
#             .values(enabled=False)
#         )
#         await self.db.execute(stmnt)
#         pressed_datasource.enabled = not pressed_datasource.enabled
#         await self.db.commit()
#         await self.db.refresh(pressed_datasource)
#         return pressed_datasource

#     async def get_enabled_source(self) -> DSMixin | None:
#         """returns the enabled datasource

#         Arguments:
#             db {AsyncSession} -- the database session
#         Returns:
#             List[DatasourceMixin] -- list of enabled datasources
#         """
#         return await self.get_by(self.model.enabled.is_(True), self.db)

#     async def require_enabled(self) -> DSMixin:
#         """returns the enabled datasource or raises an error if none is found

#         Returns:
#             DatasourceMixin -- the enabled datasource
#         """
#         enabled_source = await self.get_enabled_source()
#         if not enabled_source:
#             raise NoEnabledDatasourceError("No enabled datasource found")
#         return enabled_source

#     async def create_datasource(self, request_args: DatasourceCreateModel) -> DSMixin:
#         """given a dictionary of the kwargs to create a datasource, the datasource
#         is created and the password is encrypted before being saved to the database
#         additionally the _validate_schema method is called to validate the schema
#         which not overriden simply serializes the schema

#         Arguments:
#             obj_in {dict} -- the "model_dump" of the datasource
#             db {AsyncSession}

#         Raises:
#             BadRequest: the password was not in the request

#         Returns:
#             DatasourceReadModel -- the created datasource
#         """
#         obj_in = self._validate_schema(request_args)
#         if not "password" in obj_in:
#             raise InvalidDatasourceSchema(
#                 "You must provide a password for the datasource"
#             )
#         obj_in["password"] = crypto.encrypt_data(obj_in["password"])
#         created_model = await self.create(self.db, obj_in)
#         return created_model

#     async def update_by_id(
#         self, datasource_id: int, obj_in: dict
#     ) -> DSMixin:
#         """Given a datasource ORM instance and a dictionary of the kwargs to update
#         the datasource, the datasource is updated and the password is encrypted before
#         being saved to the database

#         Arguments:
#             db {AsyncSession}
#             datasource {DatasourceMixin}
#             obj_in {dict}

#         Raises:
#             BadRequest: the password was not in the request
#         Returns:
#             DatasourceReadModel -- the updated datasource
#         """
#         if 'enabled' in obj_in:
#             del obj_in['enabled']
#         target_datasource = await self.get_by_id(datasource_id)
#         if "password" in obj_in:
#             obj_in["password"] = crypto.encrypt_data(obj_in["password"])
#         updated_model = await self.update(self.db, target_datasource, obj_in)
#         return updated_model

#     async def test_connection(self, source: DSMixin) -> ConnectionTestResult:
#         '''Tests the connection to the datasource given a it's model
#         by creating a connection instance and testing the connection 

#         Arguments:
#             source {DatasourceMixin} -- the datasource to test

#         Returns:
#             ConnectionTestResult -- the connection test result
#         '''
#         success_msg = "Successfully connected to the datasource"
#         error_msg = "Failed to connect to the datasource"
#         error, success = await self.test_datasource_connection(source)
#         return ConnectionTestResult(
#             message=success_msg if success else error_msg,
#             success=success,
#             error=error
#         )

#     async def delete_by_id(self, datasource_id: int) -> None:
#         '''Given a datasource ID, deletes the datasource from the database
#         if it exists

#         Arguments:
#             datasource_id {int} -- the ID of the datasource to delete
#         '''
#         target_datasource = await self.get_by_id(datasource_id)
#         await self.delete(self.db, target_datasource)  

#     async def read_datasource_password(self, datasource_orm: DSMixin) -> str:
#         """Gets the decrypted password from a datasource ORM instance, only should be accesible to admins
#         updating datasources or for connecting to the datasource
#         Arguments:
#             datasource_orm {DatasourceMixin}
#         Returns:
#             str -- the decrypted password
#         """
#         decrypted_password = crypto.decrypt_data(datasource_orm.password)
#         return decrypted_password

#     async def connect_enabled(self) -> Any:
#         '''Creates a connection instance from the enabled datasource model
#         Arguments:
#             source {DatasourceMixin} -- the datasource model

#         Returns:
#             Any -- The connection instance
#         '''
#         return await self.connect(await self.require_enabled())  # type: ignore
