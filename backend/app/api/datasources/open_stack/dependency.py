

from typing import Annotated

from fastapi import Depends

from .service import OpenstackSourceService, get_openstack_service


OpenstackServiceDep = Annotated[OpenstackSourceService, Depends(
    get_openstack_service
)]
