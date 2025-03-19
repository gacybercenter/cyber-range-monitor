from typing import Annotated

from pydantic import Field

from app.extensions.datasources.schema import (
    ConnectionTestResult,
    DatasourceConnectionModel,
    DatasourceCreateForm,
    DatasourceRead,
    DatasourceUpdateForm,
    DatasourceListResponse,
    FixedStr
)


class GuacamoleRead(DatasourceRead):
    """A guacamole datasource schema from the DB"""

    datasource: Annotated[
        str, Field(..., description="The name of the Guacamole datasource")
    ]
    endpoint: Annotated[
        str, Field(..., description="The URL for the Guacamole datasource")
    ]


class GuacamoleCreateForm(DatasourceCreateForm):
    """The form for creating a new Guacamole datasource"""

    datasource: Annotated[FixedStr, Field(
        ...,
        description="The name of the Guacamole datasource"
    )]
    endpoint: Annotated[FixedStr, Field(
        ...,
        description="The URL for the Guacamole datasource"
    )]


class GuacamoleUpdateForm(DatasourceUpdateForm):
    """The form for updating a Guacamole datasource"""

    datasource: Annotated[
        FixedStr | None,
        Field(None, description="The name of the Guacamole datasource"),
    ]
    endpoint: Annotated[
        FixedStr | None,
        Field(None, description="The URL for the Guacamole datasource"),
    ]
    password: Annotated[
        FixedStr | None,
        Field(None, description="The password for the Guacamole datasource"),
    ]


class GuacamoleListResponse(DatasourceListResponse):
    """The response for listing Guacamole datasources"""
    data: list[GuacamoleRead]


class GuacamoleProtectedRead(GuacamoleRead):
    """A Guacamole datasource schema with protected fields"""
    password: Annotated[
        str,
        Field(..., description="The password for the Guacamole datasource"),
    ]


class GuacamoleSessionConfig(DatasourceConnectionModel):
    host: str 
    username: str 
    password: str 
    data_source: str
    
    
class GuacamoleConnectionResults(ConnectionTestResult):
    
    @classmethod
    def create(cls, success: bool) -> 'GuacamoleConnectionResults':
        msg = 'Sucessfully created a Guacamole session.'
        if not success:
            msg = 'Failed to create a Guacamole session likely due to improper configurations, please try again.'
        return cls(
            message=msg,
            success=success,
            error=None
        )
        
        
    
    
    
    
    


