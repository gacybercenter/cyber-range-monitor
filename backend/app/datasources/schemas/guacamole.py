from typing import Annotated

from pydantic import Field

from .base_schemas import (
    DatasourceCreateForm,
    DatasourceRead,
    DatasourceUpdateForm,
    LimitedStr,
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

    datasource: Annotated[
        LimitedStr, Field(..., description="The name of the Guacamole datasource")
    ]
    endpoint: Annotated[
        LimitedStr, Field(..., description="The URL for the Guacamole datasource")
    ]


class GuacamoleUpdateForm(DatasourceUpdateForm):
    """The form for updating a Guacamole datasource"""

    datasource: Annotated[
        LimitedStr | None,
        Field(None, description="The name of the Guacamole datasource"),
    ]
    endpoint: Annotated[
        LimitedStr | None,
        Field(None, description="The URL for the Guacamole datasource"),
    ]
    password: Annotated[
        LimitedStr | None,
        Field(None, description="The password for the Guacamole datasource"),
    ]
