
from enum import StrEnum
from typing import Annotated, Literal, Union, Dict

from fastapi import Body, Path


from ..open_stack.schema import (
    OpenstackResponse,
    OpenstackCreate,
    OpenstackUpdate,
    OpenstackListResponse
)
from ..salt_stack.schema import (
    SaltstackResponse,
    SaltstackCreate,
    SaltstackUpdate,
    SaltstackListResponse
)
from ..guac.schema import (
    GuacamoleResponse,
    GuacamoleCreate,
    GuacamoleUpdate,
    GuacamoleListResponse
)

from .examples import (
    OPENSTACK_REQUEST,
    SALTSTACK_REQUEST,
    GUAC_REQUEST,
)





ResponseSchema = Union[OpenstackResponse, SaltstackResponse, GuacamoleResponse]
CreateSchema = Union[OpenstackCreate, SaltstackCreate, GuacamoleCreate]
UpdateSchema = Union[OpenstackUpdate, SaltstackUpdate, GuacamoleUpdate]

DatasourceCreateBody = Annotated[CreateSchema, Body(
    ...,
    description="The body of the request to create a datasource",
    openapi_examples={
        'openstack': {
            'value': OPENSTACK_REQUEST
        },
        'saltstack': {
            'value': SALTSTACK_REQUEST
        },
        'guacamole': {
            'value': GUAC_REQUEST
        }
    },
    examples=[
        OPENSTACK_REQUEST,
        SALTSTACK_REQUEST,
        GUAC_REQUEST
    ]
)]

DatasourceUpdateBody = Annotated[UpdateSchema, Body(
    description="The body of the request to update a datasource",
    examples=[
        OPENSTACK_REQUEST,
        SALTSTACK_REQUEST,
        GUAC_REQUEST
    ],
    openapi_examples={
        'openstack': {
            'value': OPENSTACK_REQUEST
        },
        'saltstack': {
            'value': SALTSTACK_REQUEST
        },
        'guacamole': {
            'value': GUAC_REQUEST
        }
    }
)]





