from typing import Annotated, TypeVar
from app.core.schemas import APIListResponse, CustomBaseModel, APIRequestModel
from app.core.types import FixedStr

from pydantic import Field


class DatasourceReadModel(CustomBaseModel):
    '''the base read model for a datasource
    '''
    id: Annotated[int, Field(..., description="The ID of the datasource")]
    username: Annotated[str, Field(
        ..., description="The username for the datasource"
    )]
    enabled: Annotated[bool, Field(
        ..., description="Whether the datasource is enabled"
    )]
    endpoint: Annotated[str, Field(
        ..., description="The endpoint for the datasource"
    )]


class DatasourceCreateModel(APIRequestModel):
    '''The base create arguments for a datasource'''
    username: Annotated[
        FixedStr, Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        FixedStr, Field(..., description="The password for the datasource")
    ]
    endpoint: Annotated[
        str, Field(..., description="The endpoint for the Saltstack datasource")
    ]


class DatasourceUpdateModel(APIRequestModel):
    '''The base update model for a datasource'''
    username: Annotated[
        str | None, Field(None, description="The username for the datasource")
    ] = None
    password: Annotated[
        str | None, Field(None, description="The password for the datasource")
    ] = None
    endpoint: Annotated[str | None, Field(
        None, description="The endpoint for the Saltstack datasource"
    )] = None


DataSourceT = TypeVar('DataSourceT', bound=DatasourceReadModel)


class ConnectionTestResult(CustomBaseModel):
    '''The schema for the results of testing a datasource connection'''
    message: Annotated[str,
                       Field(..., description="The message indicating the connection result")]
    success: Annotated[bool,
                       Field(..., description="Whether the connection was successful")]
    error: Annotated[str | None, Field(
        None, description="The error message if the connection failed")]


class DatasourceConnectionModel(CustomBaseModel):
    '''Represents the arguments that when the model 
    is dumped can create a connection instance'''
    pass
