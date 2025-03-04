from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.shared.schemas import StrictModel

LimitedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]


class DatasourceRead(BaseModel):
    id: int
    username: str
    enabled: bool


class DatasourceCreateForm(StrictModel):
    username: Annotated[
        LimitedStr, Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        LimitedStr, Field(..., description="The password for the datasource")
    ]
    enabled: Annotated[
        bool, Field(..., description="Whether the datasource is enabled by default")
    ]


class DatasourceUpdateForm(StrictModel):
    username: Annotated[
        str | None, Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        str | None, Field(..., description="The password for the datasource")
    ]
