
from typing import Annotated

import guacamole
from fastapi import Depends

from range_monitor.depends import DatabaseDep, EncryptorDep
from range_monitor.guac.services.core import GuacamoleCoreService


async def get_guac_service(
    db: DatabaseDep, Encryptor: EncryptorDep
) -> GuacamoleCoreService:
    return GuacamoleCoreService(
        db=db,
        encryptor=Encryptor,
    )

async def get_active_session(
    guac_service: GuacamoleCoreService = Depends(get_guac_service),
):

    async with guac_service.session() as session:
        yield session


GuacCoreServiceDep = Annotated[GuacamoleCoreService, Depends(get_guac_service)]
ActiveGuacSessionDep = Annotated[guacamole.session, Depends(get_active_session)]
