from fastapi import APIRouter, Depends, status


from api.openapi_extra import UserAuthErrors
from app.api.users.dependency import AdminRequired


from .dependency import DatabaseHealthDep, RedisHealthDep
from .schema import (
    DatabaseHealthData,
    RedisConnectionParams,
    RedisHealthResponse,
    RedisServerStats,
)


health_router = APIRouter(
    responses=UserAuthErrors(), dependencies=[Depends(AdminRequired)]
)


@health_router.get(
    "/db", response_model=DatabaseHealthData, status_code=status.HTTP_200_OK
)
async def check_database_health(db: DatabaseHealthDep) -> DatabaseHealthData:
    """** Check Database Health ***
    _gets health related information about the database including the
    number of rows in each table, the server version, and the driver
    being used and the read time for each of the tables_

    Returns:
        DatabaseHealthData: _general health data related to redis_
    """
    return await db.get_db_info()


@health_router.get(
    "/redis/params",
    response_model=RedisConnectionParams,
    status_code=status.HTTP_200_OK,
)
async def get_redis_params(redis: RedisHealthDep) -> RedisConnectionParams:
    """** Get Redis Connection Parameters **
    Gets the connection parameters that were used to connect to the Redis server.

    Returns:
        RedisConnectionParams: _the connection parameters_
    """
    return redis.get_connection_params()


@health_router.get(
    "/redis/server", response_model=RedisServerStats, status_code=status.HTTP_200_OK
)
async def check_redis_server(redis: RedisHealthDep) -> RedisServerStats:
    """** Check Redis Server **
    _gets general health related information about the Redis server._

    _Returns_:
        RedisServerStats: _Redis server stats_
    """
    return await redis.get_server_stats()


@health_router.get(
    "/redis", response_model=RedisHealthResponse, status_code=status.HTTP_200_OK
)
async def check_redis_health(redis: RedisHealthDep) -> RedisHealthResponse:
    """** Check Redis Health ***
    gets health related information about the redis client including the
    connection status, latency, and error message if any.

    Returns:
        RedisHealthResponse: _the redis health model_
    """
    return await redis.get_redis_health()
