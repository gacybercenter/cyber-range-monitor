


from typing import Annotated

from fastapi import Depends

from range_monitor.depends import DatabaseDep, EncryptorDep
from range_monitor.guac.crud import GuacamoleRepo, GuacamoleSourceService


async def get_guacamole_repo(db: DatabaseDep) -> GuacamoleRepo:
    return GuacamoleRepo(db)

async def get_guacamole_crud(
    encryptor: EncryptorDep,
    repo: GuacamoleRepo = Depends(get_guacamole_repo),
) -> GuacamoleSourceService:
    return GuacamoleSourceService(repo, encryptor)

GuacamoleRepoDep = Annotated[GuacamoleRepo, Depends(get_guacamole_repo)]
GuacCrudServiceDep = Annotated[
    GuacamoleSourceService,
    Depends(get_guacamole_crud),
]