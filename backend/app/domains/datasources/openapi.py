
from typing import Annotated

from fastapi import Body
from .salt_stack.schema import SaltstackResponse


from .open_stack.schema import (
    OpenstackOptions,
    OpenstackUpdateOptions
)

from .guac.schema import (
    GuacamoleOptions,
    GuacamoleOptionsUpdate
)

from app.core.datasources.schema import (
    DatasourceResponse,
    DatasourceRequest,
    DatasourceUpdate
)
from app.core.schemas import APIListResponse

DSUpdateOptions = SaltstackUpdateOptions | OpenstackUpdateOptions | GuacamoleOptionsUpdate
DSOptions = SaltstackOptions | OpenstackOptions | GuacamoleOptions


GuacResponse = DatasourceResponse[GuacamoleOptions]
OpenstackResponse = DatasourceResponse[OpenstackOptions]
SaltstackResponse = DatasourceResponse[SaltstackOptions]


READ_RESPONSES = {
    200: {
        'model': GuacResponse,
        'description': 'Guacamole was used as the path parameter.'
    }, 
    200: {
        'model': OpenstackResponse,
        'description': 'Openstack was used as the path parameter.'
    },
    200: {
        'model': SaltstackResponse,
        'description': 'Saltstack was used as the path parameter.'
    }
}

LIST_RESPONSES = {
    200: {
        'model': APIListResponse[GuacResponse],
        'description': 'Guacamole was used as the path parameter.'
    },
    200: {
        'model': APIListResponse[OpenstackResponse],
        'description': 'Openstack was used as the path parameter.'
    },
    200: {
        'model': APIListResponse[SaltstackResponse],
        'description': 'Saltstack was used as the path parameter.'
    }
}

