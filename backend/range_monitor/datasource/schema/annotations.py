from typing import Annotated

from pydantic import Field

AdapterID = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier of the data source',
        min_length=1,
        max_length=36,
    ),
]


AdapterUsername = Annotated[
    str,
    Field(
        description='The username used to authenticate with the data source',
        min_length=1,
        max_length=255,
    ),
]
AdapterPassword = Annotated[
    str,
    Field(
        description='The password used to authenticate with the data source',
        min_length=1,
        max_length=255,
    ),
]



GuacamoleSource = Annotated[
    str,
    Field(
        description='The Guacamole data source identifier',
        min_length=1,
        max_length=32,
    ),
]

GuacamoleEndpoint = Annotated[
    str,
    Field(
        description='The endpoint URL of the data source',
        min_length=1,
        max_length=255,
    ),
]

AuthURL = Annotated[
    str,
    Field(
        description='The authentication URL for OpenStack',
        min_length=1,
        max_length=255,
    ),
]
UserDomainName = Annotated[
    str,
    Field(
        description='The user domain name for OpenStack',
        min_length=1,
        max_length=255,
    ),
]

RegionName = Annotated[
    str,
    Field(
        description='The region name for OpenStack',
        min_length=1,
        max_length=64,
    ),
]

APIVersion = Annotated[
    str,
    Field(
        description='The API version for OpenStack',
        min_length=1,
        max_length=8,
    ),
]


ProjectName = Annotated[
    str,
    Field(
        description='The project name for OpenStack',
        min_length=1,
        max_length=255,
    ),
]

ProjectID = Annotated[
    str,
    Field(
        description='The project ID for OpenStack',
        min_length=1,
        max_length=64,
    ),
]

ProjectDomainName = Annotated[
    str,
    Field(
        description='The project domain name for OpenStack',
        min_length=1,
        max_length=255,
    ),
]

SaltStackHostname = Annotated[
    str,
    Field(
        description='The hostname of the SaltStack master',
        min_length=1,
        max_length=255,
    ),
]
SaltstackEndpoint = Annotated[
    str,
    Field(
        description='The endpoint URL of the SaltStack master',
        min_length=1,
        max_length=255,
    ),
]