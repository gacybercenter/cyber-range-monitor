from fastapi import Depends

from typing import Annotated

from app.core.dependency import DatabaseDep

from .controller import SaltstackController

async def get_saltstack_source_service(db: DatabaseDep) -> SaltstackController:
    return SaltstackController(db)

SaltstackControllerDep = Annotated[
    SaltstackController, Depends(get_saltstack_source_service)   
]