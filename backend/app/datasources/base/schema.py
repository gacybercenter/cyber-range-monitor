from typing import Annotated, TypeVar
from app.core.schemas import APIListResponse, CustomBaseModel, APIRequestModel
from app.core.types import FixedStr 

from pydantic import Field

class DatasourceRead(CustomBaseModel):
    id: int
    username: str
    enabled: bool


class DatasourceCreateForm(APIRequestModel):
    username: Annotated[
        FixedStr, Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        FixedStr, Field(..., description="The password for the datasource")
    ]
    enabled: Annotated[
        bool, Field(..., description="Whether the datasource is enabled by default")
    ]


class DatasourceUpdateForm(APIRequestModel):
    username: Annotated[
        str | None, Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        str | None, Field(..., description="The password for the datasource")
    ]

DataSourceT = TypeVar('DataSourceT', bound=DatasourceRead)

class DatasourceListResponse(APIListResponse[DataSourceT]):
    """The response for the list of datasources"""
    data: Annotated[list[DataSourceT], Field(
        ...,
        description="The list of datasources",
    )]


    
        





