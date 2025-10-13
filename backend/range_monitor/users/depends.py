from typing import Annotated

from fastapi import Depends

from range_monitor.depends import CryptoServiceDep, DatabaseDep
from range_monitor.users.repo import UserRepository
from range_monitor.users.service import UsersService


async def get_users_repo(db: DatabaseDep) -> UserRepository:
    return UserRepository(db)


async def get_users_service(db: DatabaseDep, crypto: CryptoServiceDep) -> UsersService:
    return UsersService(
        db=db,
        crypto_service=crypto,
    )


UserRepoDep = Annotated[
    UserRepository,
    Depends(get_users_repo),
]

UsersServiceDep = Annotated[
    UsersService,
    Depends(get_users_service),
]
