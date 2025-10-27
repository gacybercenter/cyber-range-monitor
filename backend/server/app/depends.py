from collections.abc import Callable
from types import CoroutineType
from typing import Annotated, Any

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from server.db import sql
from server.db.redis import redis_client
from server.db.repos import SQLRepository
from server.external.adapters import ApiClient
from server.external.api_clients import api_client_pool
from server.external.openstack_client import OpenstackClient, openstack_client
from server.models import MappedBase

# NOTE: If you use sync dependencies, FastAPI will run them in a threadpool
# which can become really inefficient when chaining multiple dependencies together.
# So if it's non-blocking, make it async and reserve sync for blocking operations only.


async def get_redis_client() -> Redis:  # noqa: RUF029
    return redis_client


async def get_session():  # noqa: ANN201
    async with sql.get_session() as session:
        yield session


async def get_transaction_session():  # noqa: ANN201
    async with sql.get_transaction() as session:
        yield session


RedisDep = Annotated[Redis, Depends(get_redis_client)]
DatabaseDep = Annotated[AsyncSession, Depends(get_session)]
DatabaseTransactionDep = Annotated[AsyncSession, Depends(get_transaction_session)]


async def get_openstack_client() -> OpenstackClient:  # noqa: RUF029
    return openstack_client


async def ApiClientDepends(  # noqa: N802, RUF029
    api_client_name: str
) -> Callable[..., CoroutineType[Any, Any, ApiClient]]:

    async def _get_api_client(  # noqa: RUF029
        _client: str = api_client_name,
    ) -> ApiClient:
        return api_client_pool.get_client(_client)

    return _get_api_client


async def SQLRepoDepends[M: MappedBase](  # noqa: N802, RUF029
    model_type: type[M],
) -> Callable[..., CoroutineType[Any, Any, SQLRepository[M]]]:
    async def _get_sql_repo(  # noqa: RUF029
        db: DatabaseDep,
        _model_type: type[M] = model_type,
    ) -> SQLRepository[M]:
        return SQLRepository[M](
            model=_model_type,
            db=db,
        )

    return _get_sql_repo


GuacRequired = ApiClientDepends('guacamole')
SaltstackRequired = ApiClientDepends('saltstack')
OpenstackRequired = Annotated[OpenstackClient, Depends(get_openstack_client)]
