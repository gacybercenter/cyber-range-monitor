from typing import Annotated
from fastapi import Depends


from .service import SaltstackSourceService, get_saltstack_service

SaltstackServiceDep = Annotated[
    SaltstackSourceService,
    Depends(get_saltstack_service)
]
