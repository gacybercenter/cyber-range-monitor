from typing import Annotated

from pydantic import Field, StringConstraints


from app.schemas.base import APIRequestModel, CustomBaseModel

LimitedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]


class DatasourceRead(CustomBaseModel):
    id: int
    username: str
    enabled: bool


class DatasourceCreateForm(APIRequestModel):
    username: Annotated[
        LimitedStr, Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        LimitedStr, Field(..., description="The password for the datasource")
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
