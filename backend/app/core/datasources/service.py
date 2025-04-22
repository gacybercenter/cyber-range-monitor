from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import HTTPBadRequest

from .schema import (
    DatasourceRequest,
    DatasourceResponse, 
    DatasourceUpdate,
    DatasourceListResponse,
    DatasourceType
)
from .repository import DSMixin, DatasourceRepository

CreateT = TypeVar('CreateT', bound=DatasourceRequest)
UpdateT = TypeVar('UpdateT', bound=DatasourceUpdate)


class DatasourceServiceABC(ABC, Generic[DSMixin, CreateT, UpdateT]):
    """The base service class for all datasources with the shared logic
    and operations already implemented aside from custom model validation,
    creating a connection instance, and testing the connection.
    Properties:
        models {DatasourceRepository} -- the repository for the datasource model
    """

    def __init__(
        self,
        datasource_type: DatasourceType,
        model: type[DSMixin],
        db: AsyncSession
    ) -> None:
        self.models = DatasourceRepository(model, db)
        self.datasource_type: DatasourceType = datasource_type 
        
        
    @abstractmethod
    async def connect_args(self, datasource: DSMixin) -> dict:
        """given a datasource, it will resolve it's attributes into a dictionary representing
        the key word arguments to create a connection instance. 
        Arguments:
            datasource {DSMixin} -- the datasource to resolve into a connection instance
        Returns:
            dict -- the key word arguments to create a connection instance
        """

    @abstractmethod
    async def connect(self, datasource: DSMixin) -> Any:
        """turns a datasource into a connection instance, should throw if an
        error occurs or unable to resolve the datasource to a connection instance.
        Arguments:
            datasource {DSMixin} -- the datasource to connect to
        Raises:
            HTTPBadRequest -- if the datasource model cannot resolve to a connection 
            instance.
        Returns:
            Any -- the connection instance for the datasource
        """

    @abstractmethod
    async def test_connection(self, datasource: DSMixin) -> tuple[str | None, bool]:
        """tests the connection to the datasource returning an error message if it fails
        and the result of the connection test.
        Arguments:
            datasource {DSMixin} -- the datasource to test the connection to
        Returns:
            tuple[str | None, bool] -- the error message if it fails and the result of the connection test
        """
        pass

    @abstractmethod
    def to_response(self, datasource: DSMixin) -> DatasourceResponse:
        """serializes the datasource and handles nesting the options in the response.
        Arguments:
            datasource {DSMixin} -- the datasource to serialize
        Returns:
            dict -- the key word arguments to create the response model
        """

    def _http_assert_expected_type(self, input_type: DatasourceType) -> None:
        if input_type != self.datasource_type:
            raise HTTPBadRequest(
                f'Unexpected datasource type of {input_type} instead of {self.datasource_type}.' 
            )
    
    def _flatten_request_body(self, req_body: dict) -> dict:
        '''flattens the request body so that nothing is nested so the methods can be used
        Arguments:
            req_body {DatasourceRequest[OptionsT] | DatasourceUpdate[OptionsUpdateT]} -- the request body to flatten
        Returns:
            dict -- the flattened request body
        '''
        if 'options' in req_body and req_body.get('options'):
            opts = req_body.pop('options')
            req_body.update(opts)
        return req_body

    def get_base_args(self, datasource: DSMixin) -> dict:
        '''returns the DatasourceMixin base arguments in a dictionary
        for easy serialization and deserialization

        Arguments:
            datasource {DSMixin} -- the datasource to serialize

        Returns:
            dict -- the base arguments of the datasource
        '''
        return {
            'id': datasource.id,
            'username': datasource.username,
            'enabled': datasource.enabled,
            'endpoint': datasource.endpoint
        }

    async def toggle_by_id(self, id: int) -> DSMixin:
        '''toggles the enabled state of a datasource given it's 
        ID and that it exists

        Arguments:
            id {int} -- the ID of the datasource to toggle
        Raises:
            400 -- DatasourceToggleError
            HTTPNotFound -- if the datasource does not exist
        Returns:
            DSMixin -- the toggled datasource model
        '''
        model = await self.models.get_by_id(id)
        updated_model = await self.models.toggle(model)
        return updated_model

    async def create_new(self, req_body: CreateT) -> Any:
        '''creates a new datasource given the request body and validates the options 
        schema to ensure that it is validated and creates the datasource in the database.

        Arguments:
            req_body {DatasourceRequest[OptionsT]} -- the request body to create the datasource
        Raises:
            422 -- if the request body is invalid or the options schema is invalid
        Returns:
            DSMixin -- the created datasource model
        '''
        
        flattened = self._flatten_request_body(req_body.serialize())
        new_model = await self.models.create(flattened)

        return self.to_response(new_model)

    async def update_by_id(
        self,
        req_body: UpdateT,
        datasource_id: int
    ) -> Any:
        '''updates a datasource given the request body and ID and validates the options
        schema.
        Arguments:
            req_body {DatasourceUpdate[OptionsUpdateT]} -- the request body to update the datasource
            datasource_id {int} -- the ID of the datasource to update
        Raises:
            HTTPBadRequest -- if no update arguments are provided
            HTTPException(422) -- if the request body is invalid or the options schema 
            is invalid
            HTTPNotFound -- if the datasource does not exist
        Returns:
            DSMixin -- the updated datasource model
        '''
        selected_datasource = await self.models.get_by_id(datasource_id)
        flattened = self._flatten_request_body(req_body.serialize())
        
        if not flattened:
            raise HTTPBadRequest('No update arguments were provided.')
        
        updated_model = await self.models.update(selected_datasource, flattened)
        return self.to_response(updated_model)

    async def delete_by_id(self, datasource_id: int) -> None:
        '''deletes a model given it's ID and it exists
        Arguments:
            id {int} -- the ID of the model to delete
        Raises:
            HTTPNotFound -- if the model does not exist
        Returns:
            void
        '''
        model = await self.models.get_by_id(datasource_id)
        await self.models.delete(model)

    async def get_all(self) -> DatasourceListResponse:
        '''returns all the datasources in the database
        Returns:
            DatasourceListResponse -- the API list response wrapper
        '''
        db_models = await self.models.get_all_datasources()
        serialized_schemas = [self.to_response(item) for item in db_models]
        # type: ignore
        return DatasourceListResponse.from_list(serialized_schemas)
