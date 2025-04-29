from typing import Annotated, List
from pydantic import Field

from ..interface.base_schema import (
    DatasourceOptions,
    DatasourceConnectionArgs,
    DatasourceResponse,
    DatasourceCreateBody,
    DatasourceUpdateBody,
    RouterAnnotations,
    options_desc,
    DatasourceList,
    FixedStr
)


GUAC_DS_DESC = 'The name of the Guacamole datasource (e.g mysql)'
GuacDataSource = Annotated[FixedStr, Field(..., description=GUAC_DS_DESC)]


class GuacOptions(DatasourceOptions):
    '''The options for a Guacamole datasource'''
    datasource: GuacDataSource


class GuacOptionsUpdate(DatasourceOptions):
    """The optional options for updating a Guacamole datasource"""
    datasource: Annotated[
        FixedStr | None,
        Field(default=None, description=GUAC_DS_DESC),
    ]


GuacOpts = Annotated[GuacOptions, Field(
    ...,
    description=options_desc('guacamole')
)]


class GuacCreateBody(DatasourceCreateBody):
    '''The request model for creating a Guacamole datasource'''
    options: GuacOpts


class GuacUpdateBody(DatasourceUpdateBody):
    """The update model for a Guacamole datasource"""
    options: Annotated[
        GuacOptionsUpdate | None,
        Field(None, description=options_desc('guacamole'))
    ]


class GuacResponse(DatasourceResponse):
    """The response model for a Guacamole datasource, with the inherited shared attributes"""
    options: GuacOpts


class GuacListResponse(DatasourceList):
    data: Annotated[List[GuacResponse], Field(
        ...,
        description="The list of Guacamole datasources"
    )]


class GuacSessionParams(DatasourceConnectionArgs):
    '''The keyword arguments to create a guacamole.session instance'''
    host: Annotated[str, Field(
        ..., description="The Guacamole host to connect to"
    )]
    username: Annotated[str, Field(
        ..., description="The Guacamole username to connect with"
    )]
    password: Annotated[str, Field(
        ..., description="The Guacamole password to connect with"
    )]
    data_source: Annotated[str, Field(
        ..., description="The Guacamole datasource to connect to"
    )]



def create_guac_annotation() -> RouterAnnotations:
    return RouterAnnotations(
        CreateBody=GuacCreateBody,
        UpdateBody=GuacUpdateBody,
        Response=GuacResponse,
        ListResponse=GuacListResponse
    )
