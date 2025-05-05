
from typing import Annotated
from fastapi import Depends

from app.db.dependency import DatabaseDep

from .service import DatabaseHealthService, RedisHealthService




async def get_db_health_service(db: DatabaseDep) -> DatabaseHealthService:
    """Dependency to get the database health service."""
    return DatabaseHealthService(db=db)

async def get_redis_health_service() -> RedisHealthService:
    return RedisHealthService()



RedisHealthDep = Annotated[
    RedisHealthService,
    Depends(get_redis_health_service)
]
DatabaseHealthDep = Annotated[
    DatabaseHealthService,
    Depends(get_db_health_service)
]


