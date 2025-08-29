from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.common.errors import HTTPBadRequest, HTTPNotFound

from .repository import DatasourceDB, DatasourceRepository
from .base_schema import (
    DatasourceCreateBody,
    DatasourceSchema,
    DatasourceUpdateBody,
    DatasourceResponse,
    DatasourceList,
)


R = TypeVar('R', bound=DatasourceResponse)


class DatasourceServiceABC(ABC, Generic[DatasourceDB, R]):
    """The base service class for all datasources with the shared logic
    and operations already implemented aside from custom model validation,
    creating a connection instance, and testing the connection.
    Properties:
        models {DatasourceRepository} -- the repository for the datasource model
    Generics:
        DatasourceDB -- the database model representing the datasource to act on. (REQUIRED)
        R -- the response model
    """

    def __init__(
        self, *, datasource_type: str, model: Type[DatasourceDB], db: AsyncSession
    ) -> None:
        self.models = DatasourceRepository(
            model=model, db=db, datasource_type=datasource_type
        )

    @property
    def type(self) -> str:
        """returns the datasource type of the service"""
        return self.models.datasource_type  # type: ignore

    async def toggle_by_id(self, id: int) -> R:
        """toggles the enabled state of a datasource given it's
        ID and that it exists

        Arguments:
            id {int} -- the ID of the datasource to toggle
        Raises:
            400 -- DatasourceToggleError
            HTTPNotFound -- if the datasource does not exist
        Returns:
            DatasourceDB -- the toggled datasource model
        """
        model = await self.models.get_by_id(id)
        updated_model = await self.models.toggle(model)

        return self.to_response(updated_model)

    async def create(self, create_body: DatasourceCreateBody) -> R:
        """creates a new datasource given the request body and validates the options
        schema to ensure that it is validated and creates the datasource in the database.

        Arguments:
            req_body {DatasourceRequest[OptionsT]} -- the request body to create the datasource
        Raises:
            422 -- if the request body is invalid or the options schema is invalid
        Returns:
            DatasourceDB -- the created datasource model
        """

        req_body = self.validate_create_schema(create_body)
        flattened = req_body.flatten()
        new_model = await self.models.create(flattened)

        return self.to_response(new_model)

    async def update_by_id(
        self, req_body: DatasourceUpdateBody, datasource_id: int
    ) -> R:
        """updates a datasource given the request body and ID and validates the options
        schema.
        Arguments:
            req_body {UpdateT} -- the request body to update the datasource
            datasource_id {int} -- the ID of the datasource to update
        Raises:
            HTTPBadRequest -- if no update arguments are provided
            HTTPException(422) -- if the request body is invalid or the options schema
            is invalid
            HTTPNotFound -- if the datasource does not exist
        Returns:
            ResponseT -- the updated datasource model as a response
        """

        req_body = self.validate_update_schema(req_body)
        selected_datasource = await self.models.get_by_id(datasource_id)
        dump = req_body.flatten()

        if not dump:
            raise HTTPBadRequest('No update arguments were provided.')

        updated_model = await self.models.update(selected_datasource, dump)
        return self.to_response(updated_model)

    async def delete_by_id(self, datasource_id: int) -> None:
        """deletes a model given it's ID and it exists
        Arguments:
            id {int} -- the ID of the model to delete
        Raises:
            HTTPNotFound -- if the model does not exist
        """
        model = await self.models.get_by_id(datasource_id)
        await self.models.delete(model)

    async def get_datasource_list(self) -> DatasourceList:
        """returns all the datasources in the database
        Returns:
            DatasourceListResponse -- the API list response wrapper
        """
        db_models = await self.models.get_all_datasources()
        schemas = []
        for item in db_models:
            serialized = self.to_response(item)
            schemas.append(serialized)

        total = len(schemas)
        return DatasourceList(data=schemas, size=total, is_empty=(total == 0))

    async def require_enabled(self) -> DatasourceDB:
        """returns the enabled datasource or raises a 404 if no datasource is enabled

        Raises:
            HTTPNotFound: if no datasource is enabled

        Returns:
            DatasourceMixin -- the enabled datasource
        """
        enabled = await self.models.get_enabled()
        if not enabled:
            raise HTTPNotFound(self.type)
        return enabled

    async def any_enabled(self) -> bool:
        """returns true if the datasource has an enabled datasource

        Returns:
            bool -- true if the datasource has an enabled datasource
        """
        return bool(await self.models.get_enabled())

    def get_base_schema(self, db_model: DatasourceDB) -> DatasourceSchema:
        return DatasourceSchema.convert(db_model)

    # ** optional overrides **

    def validate_create_schema(
        self, schema: DatasourceCreateBody
    ) -> DatasourceCreateBody:
        """validates the options schema for the datasource, this is optional and can be overridden
        if the datasource does not require validation.
        Arguments:
            schema {UpdateT} -- the schema to validate
        Returns:
            UpdateT -- the validated schema
        """
        return schema

    def validate_update_schema(
        self, schema: DatasourceUpdateBody
    ) -> DatasourceUpdateBody:
        """validates the options schema for the datasource, this is optional and can be overridden
        if the datasource does not require validation.
        Arguments:
            schema {UpdateT} -- the schema to validate
        Returns:
            UpdateT -- the validated schema
        """
        return schema

    # ** abstract methods **

    @abstractmethod
    async def connect_args(self, datasource: DatasourceDB) -> dict:
        """given a datasource, it will resolve it's attributes into a dictionary representing
        the key word arguments to create a connection instance.
        Arguments:
            datasource {DatasourceDB} -- the datasource to resolve into a connection instance
        Returns:
            dict -- the key word arguments to create a connection instance
        """

    @abstractmethod
    async def connect(self, datasource: DatasourceDB) -> Any:
        """turns a datasource into a connection instance, should throw if an
        error occurs or unable to resolve the datasource to a connection instance.
        Arguments:
            datasource {DatasourceDB} -- the datasource to connect to
        Raises:
            HTTPBadRequest -- if the datasource model cannot resolve to a connection
            instance.
        Returns:
            Any -- the connection instance for the datasource
        """

    @abstractmethod
    async def test_connection(
        self, datasource: DatasourceDB
    ) -> tuple[str | None, bool]:
        """tests the connection to the datasource returning an error message if it fails
        and the result of the connection test.
        Arguments:
            datasource {DatasourceDB} -- the datasource to test the connection to
        Returns:
            tuple[str | None, bool] -- the error message if it fails and the result of the connection test
        """
        pass

    @abstractmethod
    def to_response(self, datasource: DatasourceDB) -> R:
        """serializes the datasource and handles nesting the options in the response.
        Arguments:
            datasource {DatasourceDB} -- the datasource to serialize
        Returns:
            dict -- the key word arguments to create the response model
        """
