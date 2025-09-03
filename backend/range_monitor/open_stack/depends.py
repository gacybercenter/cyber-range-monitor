



from typing import Annotated

from fastapi import Depends

from range_monitor.depends import DatabaseDep, EncryptorDep
from range_monitor.open_stack.services.core import OpenstackCoreService


async def get_openstack_service(
    db: DatabaseDep,
    encryptor: EncryptorDep
) -> OpenstackCoreService:
    return OpenstackCoreService(
        db=db,
        encryptor=encryptor,
    )

async def get_active_connection(
    core_service: OpenstackCoreService = Depends(get_openstack_service),
):
    async with core_service.connection() as connection:
        yield connection

OpenstackCoreServiceDep = Annotated[OpenstackCoreService, Depends(get_openstack_service)]
OpenstackConnectionDep = Annotated[dict, Depends(get_active_connection)]