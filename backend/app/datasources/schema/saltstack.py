from typing import Annotated

from pydantic import Field, HttpUrl, StringConstraints

from .base_schemas import DatasourceCreateForm, DatasourceRead, DatasourceUpdateForm

Hostname = Annotated[str, StringConstraints(min_length=1, max_length=253)]


class SaltstackRead(DatasourceRead):
    """A Saltstack datasource schema from the DB"""

    endpoint: Annotated[
        str, Field(..., description="The endpoint for the Saltstack datasource")
    ]
    hostname: Annotated[
        str, Field(..., description="The hostname for the Saltstack datasource")
    ]


class SaltstackCreateForm(DatasourceCreateForm):
    """The form for creating a new Saltstack datasource"""

    endpoint: Annotated[
        HttpUrl, Field(..., description="The endpoint for the Saltstack datasource")
    ]
    hostname: Annotated[
        Hostname, Field(..., description="The hostname for the Saltstack datasource")
    ]


class SaltstackUpdateForm(DatasourceUpdateForm):
    """The form for updating a Saltstack datasource"""

    endpoint: Annotated[
        str | None, Field(None, description="The endpoint for the Saltstack datasource")
    ]
    hostname: Annotated[
        Hostname | None,
        Field(None, description="The endpoint for the Saltstack datasource"),
    ]
