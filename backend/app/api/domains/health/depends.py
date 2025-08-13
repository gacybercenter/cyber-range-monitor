from typing import Annotated

from fastapi import Depends

from ..depends import DatabaseDep, RedisDep
from .service import DatabaseHealthService, RedisHealthService


async def get_db_health_service(db: DatabaseDep) -> DatabaseHealthService:
    """Dependency to get the database health service."""
    return DatabaseHealthService(db=db)


async def get_redis_health_service(redis: RedisDep) -> RedisHealthService:
    return RedisHealthService(redis_client=redis)


RedisHealthDep = Annotated[RedisHealthService, Depends(get_redis_health_service)]
DatabaseHealthDep = Annotated[DatabaseHealthService, Depends(get_db_health_service)]
