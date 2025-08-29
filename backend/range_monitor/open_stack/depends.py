


from typing import Annotated

from fastapi import Depends

from range_monitor.depends import DatabaseDep, EncryptorDep
from range_monitor.open_stack.crud import OpenStackRepo, OpenStackSourceService


async def get_openstack_repo(db: DatabaseDep) -> OpenStackRepo:
    return OpenStackRepo(db)

async def get_openstack_crud(
    encryptor: EncryptorDep,
    repo: OpenStackRepo = Depends(get_openstack_repo),
) -> OpenStackSourceService:
    return OpenStackSourceService(repo, encryptor)


OpenStackRepoDep = Annotated[OpenStackRepo, Depends(get_openstack_repo)]
OpenCrudServiceDep = Annotated[
    OpenStackSourceService,
    Depends(get_openstack_crud),
]