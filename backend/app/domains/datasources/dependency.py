from enum import StrEnum
from typing import Annotated, Any, Union
from fastapi import Body, Depends, Path

from app.core.errors import HTTPNotFound
from app.db.dependency import DatabaseDep
from pydantic import BaseModel



from .schema.responses import (
    GuacamoleCreate, GuacamoleUpdate,
    SaltstackCreate, SaltstackUpdate,
    OpenstackCreate, OpenstackUpdate,
    CreateSchemas, UpdateSchemas
)
from .schema.dependency import (
    DatasourceMaster, 
    ServiceContext,
    DatasourceType
)




DatasourcePath = Annotated[DatasourceType, Path(
    ...,
    description="The datasource type to act on"
)]

CreateSchemas = Union[SaltstackCreate, GuacamoleCreate, OpenstackCreate]
UpdateSchemas = Union[SaltstackUpdate, GuacamoleUpdate, OpenstackUpdate]



async def get_datasource_service(
    db: DatabaseDep,
    datasource: DatasourcePath
) -> DatasourceService:
    """resolves the path to the correct service, cannot
    function as traditional dependency due to it being dependant
    on the path parameter.

    Arguments:
        db {DatabaseDep} -- the database dependency
        datasource {DatasourcePath} -- the datasource type

    Returns:
        DatasourceService -- the service to use for the datasource
    """

    service = None
    match datasource:
        case Datasources.OPEN_STACK:
            service = OpenstackSourceService(db)

        case Datasources.GUAC:
            service = GuacamoleSourceService(db)

        case Datasources.SALT_STACK:
            service = SaltstackSourceService(db)

        case _:
            raise HTTPNotFound("Unknown and unsupported datasource.")

    return service


async def get_valid_create_schema(
    datasource: DatasourcePath,
    data: dict[str, Any] = Body(...)
) -> CreateSchemas:
    match datasource:
        case Datasources.OPEN_STACK:
            return OpenstackCreate(**data)

        case Datasources.GUAC:
            return GuacamoleCreate(**data)

        case Datasources.SALT_STACK:
            return SaltstackCreate(**data)

        case _:
            raise HTTPNotFound("Unknown and unsupported datasource.")


async def get_valid_update_schema(
    datasource: DatasourcePath,
    data: dict[str, Any] = Body(...)
) -> UpdateSchemas:
    match datasource:
        case Datasources.OPEN_STACK:
            return OpenstackUpdate(**data)

        case Datasources.GUAC:
            return GuacamoleUpdate(**data)

        case Datasources.SALT_STACK:
            return SaltstackUpdate(**data)

        case _:
            raise HTTPNotFound("Unknown and unsupported datasource.")




DatasourceServiceDep = Annotated[DatasourceService, Depends(get_datasource_service)]
DatasourceCreateDep = Annotated[CreateSchemas, Depends(get_valid_create_schema)]
DatasourceUpdateDep = Annotated[UpdateSchemas, Depends(get_valid_update_schema)]

DatasourceResponseSchema = Union[
    OpenstackResponse,
    GuacamoleResponse,
    SaltstackResponse
]

DatasourceListResponses = Union[
    OpenstackResponse,
    GuacamoleResponse,
    SaltstackResponse
]







# def annotate_list_response_types() -> Dict:
#     return {
#         200: {
#             'description': 'The response body for the datasource',
#             'content': {
#                 'application/json': {
#                     'schema': {
#                         'oneOf': [
#                               {'$ref': '#/components/schemas/OpenstackListResponse'},
#                             {'$ref': '#/components/schemas/SaltstackListResponse'},
#                             {'$ref': '#/components/schemas/GuacamoleListResponse'}
#                         ]
#                     }
#                 }
#             }
#         }
#     }
