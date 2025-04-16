from typing import Annotated, Any, Callable, Type, TypeVar, NewType

from fastapi import APIRouter, Body, Depends, Security, dependencies, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions.openapi_extra import ROLE_REQUIRED_DEP_RESPONSE


from app.core.dependency import DatabaseDep
from app.core.schemas import APIListResponse, GenericAPIResponse
from app.core.types import PathID


from app.extensions.openapi_extra.responses import NOT_FOUND_404
from app.users.dependency import (
    AdminRequired, RoleRequired, UserRequired
)
from fastapi.routing import APIRoute


from .base.controller import DatasourceController
from .base.schema import (
    ConnectionTestResult,
    DatasourceCreateModel,
    DatasourceReadModel,
    DatasourceUpdateModel
)

from .schema import Datasources
from .const import NOT_ENABLED_RESPONSE, TOGGLE_ERROR_RESPONSE


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


class DatasourceRouter:
    '''The shared routes and behavior across all datasources'''

    def __init__(
        self,
        service: type[DatasourceController],
        source_type: Datasources,
        create_model: type[DatasourceCreateModel],
        read_model: type[DatasourceReadModel],
        update_model: type[DatasourceUpdateModel]
    ) -> None:
        self.source_type = source_type

        self.service = service
        self.create_model = create_model
        self.read_model = read_model
        self.update_model = update_model

    def create_api_router(self) -> APIRouter:
        return APIRouter(
            prefix=f'/{self.source_type.value}',
            tags=[self.source_type],
            dependencies=[Security(RoleRequired)],
            responses=ROLE_REQUIRED_DEP_RESPONSE,
            generate_unique_id_function=unique_id_fn(self.source_type)
        )

    async def service_dep(self, db: DatabaseDep):
        return self.service(db)


def create_router(
    router_config: DatasourceRouter
) -> APIRouter:
    '''Creates a router given a datasource service and returns 
    the router with the routes added.

    Arguments:
        router_config {DatasourceRouter} -- the router config

    Returns:
        APIRouter -- the router with the shared routes
    '''

    ReadModel = router_config.read_model
    CreateBody = router_config.create_model
    UpdateBody = router_config.update_model
    DatasourceList = APIListResponse[ReadModel]

    router = router_config.create_api_router()

    ServiceDep = Depends(router_config.service_dep)

    @router.get(
        '/',
        response_model=DatasourceList,
        responses=NOT_FOUND_404
    )
    async def get_all_datasources(
        service: DatasourceController = Depends(router_config.service_dep)
    ) -> APIListResponse:
        return await service.get_all_sources()

    @router.post('/', response_model=ReadModel, dependencies=[Security(AdminRequired)])
    async def create_datasource(
        create_body: CreateBody = Body(...),  # type: ignore
        service: DatasourceController = ServiceDep
    ) -> ReadModel:  # type: ignore
        model = await service.create_datasource(create_body)
        return service.serialize(model)

    @router.patch(
        '/{source_id}/',
        response_model=ReadModel,
        responses=NOT_FOUND_404,
        dependencies=[Security(AdminRequired)]
    )
    async def update_source_id(
        source_id: PathID,
        update_body: UpdateBody = Body(),  # type: ignore
        service: DatasourceController = ServiceDep
    ) -> ReadModel:  # type: ignore

        new_model = await service.update_by_id(
            source_id, update_body
        )
        return service.serialize(new_model)

    @router.delete(
        '/{source_id}/',
        response_model=GenericAPIResponse,
        responses=NOT_FOUND_404,
        dependencies=[Security(AdminRequired)]
    )
    async def delete_source_id(
        source_id: PathID,
        service: DatasourceController = ServiceDep
    ) -> GenericAPIResponse:
        await service.delete_by_id(source_id)
        return GenericAPIResponse(
            message=f"Datasource {source_id} deleted successfully",
            data={"id": source_id}
        )

    @router.get('/{source_id}/', response_model=ReadModel, responses=NOT_FOUND_404)
    async def read_source_id(
        source_id: PathID,
        service: DatasourceController = ServiceDep
    ) -> ReadModel:  # type: ignore
        model = await service.get_by_id(source_id)
        return service.serialize(model)

    @router.post('/enable/{source_id}', response_model=ReadModel, responses=NOT_FOUND_404)
    async def enable_source_id(
        source_id: PathID,
        service: DatasourceController = ServiceDep
    ) -> ReadModel:  # type: ignore
        model = await service.get_by_id(source_id)
        new_model = await service.enable(model)
        return service.serialize(new_model)

    @router.post('/disable', response_model=ReadModel, responses=NOT_ENABLED_RESPONSE)
    async def disable_source_id(
        source_id: PathID,
        service: DatasourceController = ServiceDep
    ) -> ReadModel:  # type: ignore
        enabled = await service.require_enabled()
        new_model = await service.disable(enabled)
        return service.serialize(new_model)

    @router.post('/toggle/{source_id}', response_model=ReadModel, responses=TOGGLE_ERROR_RESPONSE)
    async def toggle_source_id(
        source_id: PathID,
        service: DatasourceController = ServiceDep
    ) -> ReadModel:  # type: ignore
        model = await service.toggle(source_id)
        return service.serialize(model)

    @router.get('/test/{source_id}', response_model=ConnectionTestResult, responses=NOT_ENABLED_RESPONSE)
    async def test_connection_id(
        source_id: PathID,
        service: DatasourceController = ServiceDep
    ) -> ConnectionTestResult:
        model = await service.get_by_id(source_id)
        return await service.test_connection(model)

    @router.get('/test', response_model=ConnectionTestResult, responses=NOT_ENABLED_RESPONSE)
    async def test_connection(service: DatasourceController = ServiceDep) -> ConnectionTestResult:
        enabled_source = await service.require_enabled()
        return await service.test_connection(enabled_source)

    return router

''' NOTE: to the person attempting to refactor the function above -^^

i know this solution isn't ideal and is hacky, but I spent an unhealthy amount of time 
trying not to repeat the same code for each datasource route while preserving the OpenAPI
types for each request.

if you attempt to fix this read the following to avoid wasting your time
about the following insanity inducing quirk I had to discover about pydantic or 
ignore if not since it's hyper specific to this use case.

dynamically created types would be generics such as TypeVar and NewType().
However pydantic generates type annotations statically meaning dynamic types are 
not inferred at run time.

meaning if you have a generic type var like this 

    class base(BaseModel):
        foo: int 
    
    class bar(base):
        data: any
        
    class baz(base):
        foobar: str
    
and then use that type var to dynamically create types like this

def router[T: base](route_prefix: str):
    router = APIRouter(
        prefix=route_prefix
    )
    
    x = bar(foo=1, data=2)
    y = baz(foo=7, foobar="hello")
    
    @router.get("/{child}", response_model=T)
    async def get_data(child: Literal["bar", "baz"]):
        if child == "bar":
            return x
        else:
            return y
    
    (...)

the openapi documentation will only recognize the type bound to T which is "base"
thus the response model will be  

{
    "foo": int
}

which ruins the consistency and automation provided by openapi.

the alternative (logically) is nesting generics in each of the classes for the required 
type annotations (more than i already did) which becomes really messy, but i still tried 
that more than once and you end up with about one # type: ignore per every 5 lines and code 
harder to read than a minecraft enchantment table.

thank you for reading my soliloquy 

hours wasted:
    - ryan: 17
    
'''
