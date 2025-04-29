from typing import Annotated, Generic, Literal

from pydantic import Field, ConfigDict


from typing import TypeVar

from app.common.schemas.http import RequestSchema, CustomBaseModel, ResponseList, ResponseSchema
from common.types import FixedStr


class DatasourceOptions(ResponseSchema):
    pass


class DatasourceOptionsUpdate(RequestSchema):
    '''The base update model for a datasource options'''
    pass


class DatasourceConnectionArgs(CustomBaseModel):
    '''Represents the arguments that when the model 
    is dumped can create a connection instance'''


OptionsT = TypeVar('OptionsT', bound=DatasourceOptions)
OptionsUpdateT = TypeVar('OptionsUpdateT', bound=DatasourceOptionsUpdate)


class DatasourceResponse(ResponseSchema, Generic[OptionsT]):
    '''The datasource returned from the API
    Arguments:
        Generic {OptionsT} -- the model representing the options
        of the datasource
    '''
    username: Annotated[FixedStr, Field(
        ...,
        description="The username for the datasource"
    )]
    endpoint: Annotated[FixedStr, Field(
        ...,
        description="The endpoint for the datasource"
    )]
    id: Annotated[int, Field(..., description="The ID of the datasource")]

    options: Annotated[OptionsT, Field(
        ..., description="The options for the datasource"
    )]

    enabled: Annotated[bool, Field(
        ..., description="Whether the datasource is enabled"
    )]


ResponseT = TypeVar('ResponseT', bound=DatasourceResponse)


class DatasourceRequest(RequestSchema, Generic[OptionsT]):
    '''The base request model for a datasource
    Arguments:
        Generic {OptionsT} -- the model representing the options
        of the datasource
    '''
    username: Annotated[FixedStr, Field(
        ...,
        description="The username for the datasource"
    )]
    
    endpoint: Annotated[FixedStr, Field(
        ...,
        description="The endpoint for the datasource"
    )]
    
    password: Annotated[FixedStr, Field(
        ..., 
        description="The password for the datasource"
    )]
    
    options: Annotated[OptionsT, Field(
        ..., 
        description="The options for the datasource"
    )]


class DatasourceUpdate(RequestSchema, Generic[OptionsUpdateT]):
    '''The base update model for a datasource
    Arguments:
        Generic {OptionsT} -- the model representing the options
        of the datasource with them being optional
    '''
    username: Annotated[str | None, Field(
        None, description="The username for the datasource"
    )] = None
    password: Annotated[str | None, Field(
        None,
        description="The password for the datasource"
    )] = None
    endpoint: Annotated[str | None, Field(
        None,
        description="The endpoint for the Saltstack datasource"
    )] = None
    options: Annotated[OptionsUpdateT | None, Field(
        None,
        description="The options for the datasource"
    )] = None


class DatasourceListResponse(ResponseList[ResponseT]):
    '''The response model for a list of datasources'''
    any_enabled: Annotated[bool, Field(
        ...,
        description="Whether any of the datasources are enabled"
    )] = False
    data: Annotated[list[ResponseT], Field(
        ...,
        description="The list of datasources"
    )]