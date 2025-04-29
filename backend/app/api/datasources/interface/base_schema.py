from typing import Annotated, List, Type, TypeVar, Generic
from app.common.schemas.http import (
    RequestSchema,
    ResponseSchema,
    ResponseList,
    CustomBaseModel
)
from pydantic import Field

from app.common.types import FixedStr


DSUsername = Annotated[
    FixedStr,
    Field(..., description="The username of the datasource")
]
DSPassword = Annotated[
    FixedStr,
    Field(..., description="The password of the datasource")
]
DSEndpoint = Annotated[
    FixedStr,
    Field(..., description="The endpoint of the datasource")
]


class DatasourceSchema(ResponseSchema):
    id: Annotated[int, Field(
        ...,
        description="The ID of the datasource"
    )]
    enabled: Annotated[bool, Field(
        ...,
        description="Whether the datasource is enabled or not"
    )]
    username: DSUsername
    password: DSPassword
    endpoint: DSEndpoint


class DatasourceAuth(RequestSchema):
    '''The shared attributes for all of the Datasource models'''
    username: DSUsername
    password: DSPassword
    endpoint: DSEndpoint


class DatasourceAuthUpdate(RequestSchema):
    '''The shared attributes for all of the Datasource models as optional arguments'''
    username: Annotated[FixedStr | None, Field(
        default=None,
        description="The username of the datasource"
    )]

    password: Annotated[FixedStr | None, Field(
        default=None,
        description="The password of the datasource"
    )]

    endpoint: Annotated[FixedStr | None, Field(
        default=None,
        description="The endpoint of the datasource"
    )]


class DatasourceOptions(RequestSchema):
    '''The options for the datasource'''


class DatasourceConnectionArgs(CustomBaseModel):
    '''The arguments to create a connection to the datasource'''


DSO = TypeVar('DSO', bound=DatasourceOptions)


DataSourceDict = Annotated[
    DatasourceSchema,
    Field(..., description="The shared attributes for all of the Datasource models")
]

DSOptions = Annotated[
    DatasourceOptions,
    Field(..., description="The custom / unique options for the datasource")
]


class DatasourceResponse(ResponseSchema):
    '''The response model for a datasource'''
    data_source: DataSourceDict
    options: DSOptions


class DatasourceList(ResponseList):
    data: Annotated[List[DatasourceResponse], Field(
        ...,
        description="The list of datasources"
    )]


class DatasourceBodyMixin(RequestSchema):
    def flatten(self) -> dict:
        '''flattens the request body so that nothing is nested so the methods can be used
        Arguments:
            req_body {DatasourceRequest[OptionsT] | DatasourceUpdate[OptionsUpdateT]} -- the request body to flatten
        Returns:
            dict -- the flattened request body
        '''
        schema = self.serialize()
        for attrs in ('data_source', 'options'):
            if attrs in schema:
                attr = schema.pop(attrs)
                schema.update(attr)
        return schema


class DatasourceCreateBody(DatasourceBodyMixin):
    '''The request body to create a new datasource'''
    data_source: Annotated[
        DatasourceAuth,
        Field(..., description="The shared attributes for all of the Datasource models")
    ]
    options: DSOptions


class DatasourceUpdateBody(DatasourceBodyMixin):
    '''The request body to update a datasource'''
    data_source: Annotated[
        DatasourceAuthUpdate | None,
        Field(
            default=None,
            description="The shared attributes for all of the Datasource models"
        )
    ]

    options: Annotated[DatasourceOptions | None, Field(
        default=None,
        description="The custom / unique options for the datasource"
    )]


def options_desc(ds_type: str) -> str:
    '''returns the description for the options field in the request body'''
    return f"The options for the {ds_type} datasource"


class RouterAnnotations(CustomBaseModel):
    '''The type annotations for creating a datasource router'''
    CreateBody: Type[DatasourceCreateBody]
    UpdateBody: Type[DatasourceUpdateBody]
    Response: Type[DatasourceResponse]
    ListResponse: Type[DatasourceList]
    
    
class ConnectionTestResults(ResponseSchema):
    message: Annotated[
        FixedStr,
        Field(..., description="The message of the connection test")
    ]
    success: Annotated[
        bool,
        Field(..., description="Whether the connection test was successful or not")
    ]
    