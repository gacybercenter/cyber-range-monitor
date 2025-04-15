

from fastapi import APIRouter, Security, status
from app.extensions.openapi_extra import ROLE_REQUIRED_DEP_RESPONSE


from typing import Callable, Generic, TypeVar

from app.core.dependency import DatabaseDep
from app.core.schemas import GenericAPIResponse
from app.core.types import PathID


from app.extensions.openapi_extra.responses import NOT_FOUND_404
from app.users.dependency import (
    AdminRequired, RoleRequired, UserRequired
)
from fastapi.routing import APIRoute

from .base.controller import DatasourceController
from .base.schema import (
    ConnectionTestResult,
    DatasourceReadModel,
    DatasourceUpdateModel,
    DatasourceListResponse
)

from .schema import Datasources
from .const import NOT_ENABLED_RESPONSE, TOGGLE_ERROR_RESPONSE


ReadModelT = TypeVar('ReadModelT', bound=DatasourceReadModel)
UpdateModelT = TypeVar('UpdateModelT', bound=DatasourceUpdateModel)


def unique_id_fn(datasource: Datasources) -> Callable[[APIRoute], str]:
    '''closure to create a unique operation ID for the datasource 
    routes to avoid operation ID conflicts for OpenAPI

    Arguments:
        datasource {Datasources} -- the datasource type

    Returns:
        Callable[[APIRoute], str] -- the closure to create a unique
        operation ID 
    '''
    def create_operation_id(route: APIRoute) -> str:
        return f'{datasource}-{route.name}'
    return create_operation_id


class DatasourceRouter(Generic[ReadModelT, UpdateModelT]):
    '''The shared routes and behavior across all datasources

    Arguments:
        Generic {ReadModelT, UpdateModelT} -- the response types for the datasource
    '''

    def __init__(
        self,
        service: type[DatasourceController],
        source_type: Datasources
    ) -> None:
        self.router = APIRouter(
            prefix=f'/{source_type.value}',
            tags=[source_type],
            dependencies=[Security(RoleRequired)],
            responses=ROLE_REQUIRED_DEP_RESPONSE,
            generate_unique_id_function=unique_id_fn(source_type)
        )
        self.service = service
        self.source_type = source_type

    def register_routes(self) -> APIRouter:
        '''registers the routes for the datasource router using the class methods'''
        # create
        self.router.add_api_route(
            '/',
            endpoint=self.create_datasource,
            response_model=ReadModelT,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Security(AdminRequired)],
            methods=['POST']
        )

        # get all
        self.router.add_api_route(
            '/',
            endpoint=self.get_all_datasources,
            response_model=DatasourceListResponse[ReadModelT],
            responses=NOT_FOUND_404,
            methods=['GET']
        )

        # read by id
        self.router.add_api_route(
            '/{source_id}',
            endpoint=self.get_datasource_by_id,
            response_model=ReadModelT,
            responses=NOT_FOUND_404,
            methods=['GET']
        )

        # toggle
        self.router.add_api_route(
            '/toggle/{source_id}',
            endpoint=self.toggle_datasource,
            response_model=ReadModelT,
            responses=TOGGLE_ERROR_RESPONSE,
            dependencies=[Security(UserRequired)],
            methods=['POST']
        )

        # test enabled connection
        self.router.add_api_route(
            '/test',
            endpoint=self.test_connection,
            response_model=GenericAPIResponse,
            responses=NOT_ENABLED_RESPONSE,
            methods=['GET']
        )

        # test connection by ID
        self.router.add_api_route(
            '/test/{source_id}',
            endpoint=self.test_datasource_connection,
            response_model=GenericAPIResponse,
            responses=NOT_FOUND_404,
            methods=['GET']
        )

        # update datasource
        self.router.add_api_route(
            '/{source_id}',
            endpoint=self.update_datasource,
            methods=['PATCH'],
            response_model=ReadModelT,
            responses=NOT_FOUND_404
        )

        # delete datasource
        self.router.add_api_route(
            '/{source_id}',
            endpoint=self.delete_datasource,
            response_model=GenericAPIResponse,
            responses=NOT_FOUND_404,
            methods=['DELETE']
        )

        return self.router

    async def get_all_datasources(self, db: DatabaseDep) -> DatasourceListResponse[ReadModelT]:
        '''returns a list of all of the datasources of the given type

        Arguments:
            db {DatabaseDep} -- the database dependency

        Returns:
            DatasourceListResponse[ReadModelT] -- the list of all datasources
        '''
        service = self.service(db)
        return await service.get_all_sources()  # type: ignore

    async def get_datasource_by_id(self, source_id: PathID, db: DatabaseDep) -> ReadModelT:
        '''gets a datasource by its id

        Arguments:
            db {DatabaseDep} -- the database dependency
            source_id {int} -- the id of the datasource

        Returns:
            ReadModelT -- the datasource
        '''
        service = self.service(db)
        source = await service.get_by_id(source_id)
        return service.serialize(source)  # type: ignore

    async def create_datasource(self, db: DatabaseDep, source_data: ReadModelT) -> ReadModelT:
        '''creates a new datasource

        Arguments:
            db {DatabaseDep} -- the database dependency
            source_data {ReadModelT} -- the data to create the datasource

        Returns:
            ReadModelT -- the created datasource
        '''
        service = self.service(db)
        source = await service.create_datasource(source_data)
        return service.serialize(source)  # type: ignore

    async def update_datasource(
        self,
        source_id: PathID,
        source_data: UpdateModelT,
        db: DatabaseDep
    ) -> ReadModelT:
        '''Updates a datasource by its id

        Arguments:
            source_id {PathID} -- the id of the datasource
            source_data {UpdateModelT} -- the data to update the datasource with
            db {DatabaseDep} -- the database dependency

        Returns:
            ReadModelT -- the updated datasource
        '''
        service = self.service(db)
        return await service.update_by_id(
            source_id,
            source_data.serialize()
        )  # type: ignore

    async def delete_datasource(self, source_id: PathID, db: DatabaseDep) -> GenericAPIResponse:
        '''deletes a datasource by its id

        Arguments:
            source_id {PathID} -- the ID of the datasource to delete
            db {DatabaseDep} -- the database dependency

        Returns:
            GenericAPIResponse -- the API response model with a message and the ID of the deleted datasource
        '''
        service = self.service(db)
        await service.delete_by_id(source_id)
        return GenericAPIResponse(
            message=f"Datasource {source_id} deleted successfully",
            data={"id": source_id}
        )

    async def toggle_datasource(self, source_id: PathID, db: DatabaseDep) -> ReadModelT:
        '''toggles the enabled datasource

        Arguments:
            source_id {PathID} -- the ID of the datasource to toggle
            db {DatabaseDep} -- the database dependency

        Returns:
            ReadModelT -- the toggled datasource
        '''
        service = self.service(db)
        pressed_model = await service.toggle_by_id(source_id)
        return service.serialize(pressed_model)  # type: ignore

    async def test_datasource_connection(self,  source_id: PathID, db: DatabaseDep) -> ConnectionTestResult:
        '''tests the connection of a datasource by its id

        Arguments:
            db {DatabaseDep} -- the database dependency
            source_id {int} -- the id of the datasourceq

        Returns:
            ConnectionTestResult -- the result of the connection test
        '''
        service = self.service(db)
        model = await service.get_by_id(source_id)
        result = await service.test_connection(model)
        return result

    async def test_connection(self, db: DatabaseDep) -> ConnectionTestResult:
        '''tests the connection of the datasource

        Arguments:
            db {DatabaseDep} -- tests the connection of the datasource

        Returns:
            ConnectionTestResult -- the result of the connection test
        '''
        service = self.service(db)
        enabled_source = await service.require_enabled()
        return await service.test_connection(enabled_source)  # type: ignore
