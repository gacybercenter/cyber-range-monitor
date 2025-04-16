from typing import Annotated

from pydantic import Field

from app.datasource.base.schema import (
    DatasourceConnectionModel,
    DatasourceCreateModel,
    DatasourceReadModel,
    DatasourceUpdateModel,
    FixedStr
)


class GuacamoleRead(DatasourceReadModel):
    """A guacamole datasource schema from the DB"""
    datasource: Annotated[
        str, Field(..., description="The name of the Guacamole datasource")
    ]


class GuacamoleCreate(DatasourceCreateModel):
    """The data for creating a new Guacamole datasource"""
    datasource: Annotated[FixedStr, Field(
        ...,
        description="The name of the Guacamole datasource"
    )]


class GuacamoleUpdate(DatasourceUpdateModel):
    """The data for updating a Guacamole datasource"""
    datasource: Annotated[
        FixedStr | None,
        Field(None, description="The name of the Guacamole datasource"),
    ] = None


class GuacamoleSessionConfig(DatasourceConnectionModel):
    '''keyword arguments to create a guacamole.session instance'''
    host: Annotated[str,
                    Field(..., description="The Guacamole host to connect to")]
    username: Annotated[str,
                        Field(..., description="The Guacamole username to connect with")]
    password: Annotated[str,
                        Field(..., description="The Guacamole password to connect with")]
    data_source: Annotated[str,
                           Field(..., description="The Guacamole datasource to connect to")]
