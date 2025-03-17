from fastapi import Depends

from typing import Annotated

from app.core.dependency import DatabaseDep

from .controller import OpenstackController


async def get_openstack_source_service(db: DatabaseDep) -> OpenstackController:
    return OpenstackController(db)


OpenstackControllerDep = Annotated[
    OpenstackController, Depends(get_openstack_source_service)
]

