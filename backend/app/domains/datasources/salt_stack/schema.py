from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.core.datasources.schema import (
    DatasourceListResponse,
    DatasourceOptions, 
    DatasourceOptionsUpdate,
    DatasourceConnectionArgs,
    DatasourceRequest,
    DatasourceResponse,
    DatasourceUpdate
)


class SaltstackOptions(DatasourceOptions):
    '''The options for creating a saltstack datasource'''
    hostname: Annotated[str, Field(
        ...,
        description="The hostname of the saltstack datasource."
    )]
    
class SaltstackUpdateOptions(DatasourceOptionsUpdate):
    '''The options for updating a saltstack datasource'''
    hostname: Annotated[str | None, Field(
        None,
        description="The hostname of the saltstack datasource."
    )] = None

class SaltstackCreate(DatasourceRequest[SaltstackOptions]):
    '''The request model for creating a saltstack datasource'''
    pass

class SaltstackUpdate(DatasourceUpdate[SaltstackUpdateOptions]):
    '''The request model for updating a saltstack datasource'''
    pass

class SaltstackResponse(DatasourceResponse[SaltstackOptions]):
    '''The response model for a saltstack datasource'''
    pass

class SaltstackListResponse(DatasourceListResponse[SaltstackResponse]):
    '''The response model for a list of saltstack datasources'''
    pass


# TODO not implemented
class SaltstackConnectionArgs(DatasourceConnectionArgs):
    '''The connection args for a saltstack datasource'''
    # hostname: Annotated[str, Field(
    #     ...,
    #     description="The hostname of the saltstack datasource."
    # )] = Field(..., alias="host")
