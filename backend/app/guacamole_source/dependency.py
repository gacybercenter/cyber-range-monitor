from fastapi import Depends

from typing import Annotated

from app.core.dependency import DatabaseDep

from .controller import GuacamoleController


async def get_guac_controller(db: DatabaseDep) -> GuacamoleController:
    return GuacamoleController(db)

GuacControllerDep = Annotated[
    GuacamoleController, Depends(get_guac_controller)
]
