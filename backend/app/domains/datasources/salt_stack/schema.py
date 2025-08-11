from typing import Annotated, List

from pydantic import Field

from ..interface.base_schema import (
    DatasourceList,
    DatasourceOptions,
    DatasourceConnectionArgs,
    DatasourceResponse,
    DatasourceCreateBody,
    DatasourceUpdateBody,
    FixedStr,
    RouterAnnotations,
    options_desc,
)


HOSTNAME_DESC = "The hostname of the saltstack datasource."

Hostname = Annotated[FixedStr, Field(..., description=HOSTNAME_DESC)]


class SaltstackOptions(DatasourceOptions):
    """The options for creating a saltstack datasource"""

    hostname: Hostname


class SaltstackOptionsUpdate(DatasourceOptions):
    """The options for updating a saltstack datasource"""

    hostname: Annotated[
        FixedStr | None,
        Field(None, description="The hostname of the saltstack datasource."),
    ]


SaltStackOpts = Annotated[
    SaltstackOptions, Field(..., description=options_desc("saltstack"))
]


class SaltstackCreateBody(DatasourceCreateBody):
    """The request model for creating a saltstack datasource"""

    options: SaltStackOpts


class SaltstackUpdateBody(DatasourceUpdateBody):
    """The request model for updating a saltstack datasource"""

    options: Annotated[
        SaltstackOptionsUpdate | None,
        Field(None, description=options_desc("saltstack")),
    ]


class SaltstackResponse(DatasourceResponse):
    """The response model for a saltstack datasource"""

    options: SaltStackOpts


class SaltstackListResponse(DatasourceList):
    """The response model for a list of saltstack datasources"""

    data: Annotated[
        List[SaltstackResponse],
        Field(..., description="The list of saltstack datasources"),
    ]


# TODO not implemented


class SaltstackConnectionArgs(DatasourceConnectionArgs):
    """The connection args for a saltstack datasource"""

    # hostname: Annotated[str, Field(
    #     ...,
    #     description="The hostname of the saltstack datasource."
    # )] = Field(..., alias="host")


def create_saltstack_annotation() -> RouterAnnotations:
    return RouterAnnotations(
        CreateBody=SaltstackCreateBody,
        UpdateBody=SaltstackUpdateBody,
        Response=SaltstackResponse,
        ListResponse=SaltstackListResponse,
    )
