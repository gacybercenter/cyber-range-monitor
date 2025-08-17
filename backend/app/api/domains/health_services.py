import time
from datetime import datetime, timezone
from typing import Any

import aiosqlite
import redis.asyncio as aioredis
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.redis.settings import redis_secrets

from ..schemas.health import (
    DatabaseHealthData,
    DatabaseTableMeta,
    RedisConnectionParams,
    RedisHealthResponse,
    RedisServerStats,
)


class DatabaseHealthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_server_version(self) -> Any:
        """Returns the server version of the database."""
        result = await self.db.execute(text('SELECT sqlite_version()'))
        return result.scalar()

    async def get_model_metadata(self, model: Any) -> DatabaseTableMeta:
        """gets metadata about a database model including the number of rows
        the time it took to read and the name of the table.

        Args:
            model (Any): _the model to read from_

        Returns:
            DatabaseTableMeta: _the meta data about the database model_
        """
        table_name = model.__tablename__
        read_start = time.perf_counter()
        statement = select(func.count()).select_from(model)  # type: ignore
        result = await self.db.execute(statement)
        row_count = result.scalar_one()
        read_time = time.perf_counter() - read_start
        return DatabaseTableMeta(
            table_name=table_name, row_count=row_count, read_time=read_time
        )

    async def get_db_info(self) -> DatabaseHealthData:
        from app.infrastructure.db import iter_db_models

        model_data = [
            await self.get_model_metadata(model) for model in iter_db_models()
        ]
        server_version = await self.get_server_version()
        driver_info = aiosqlite.__version__
        return DatabaseHealthData(
            server_version=server_version,
            driver=f'SQLite {driver_info}',
            table_meta=model_data,
        )


class RedisHealthService:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.client: aioredis.Redis = redis

    def get_connection_params(self) -> RedisConnectionParams:
        """
        Retrieves the connection parameters for the Redis client.

        Returns
        -------
        RedisConnectionParams
            The connection parameters including host,
            port, db, and client_id.
        """
        client_id = None
        try:
            client_id = self.client.client_id()
        except Exception:
            pass
        return RedisConnectionParams(
            host=redis_secrets.HOST,
            port=redis_secrets.PORT,
            db=redis_secrets.DB,
            client_id=client_id,
        )

    async def get_server_stats(self) -> RedisServerStats:
        """
        Retrieves Redis server statistics including memory usage, uptime,
        and connection info.

        Returns
        -------
        RedisServerStats
        """

        redis_info: dict = await self.client.info()

        uptime_seconds = redis_info.get('uptime_in_seconds', 0)
        used_memory = redis_info.get('used_memory_human', '0B')
        used_memory_peak = redis_info.get('used_memory_peak_human', '0B')
        connected_clients = int(redis_info.get('connected_clients', 0))

        connection_info = self.get_connection_params()
        total_connections = int(redis_info.get('total_connections_received', 0))
        connected_clients = int(redis_info.get('connected_clients', 0))

        rejected_connections = int(redis_info.get('rejected_connections', 0))
        return RedisServerStats(
            used_memory=used_memory,
            used_memory_peak=used_memory_peak,
            uptime_seconds=uptime_seconds,
            total_connections=total_connections,
            connected_clients=connected_clients,
            rejected_connections=rejected_connections,
            connection_info=connection_info,
        )

    def _calc_latency(self, start_time: float) -> float:
        """Calculates the latency in ms."""
        return (time.perf_counter() - start_time) * 1000

    async def get_redis_health(self) -> RedisHealthResponse:
        """
        Checks the health of the Redis server by pinging it and measuring latency.

        Returns
        -------
        RedisHealthResponse
        """

        start_time = time.perf_counter()
        connected = False
        error = None
        try:
            connected = await self.client.ping()
            latency_ms = self._calc_latency(start_time)
            status = 'healthy' if latency_ms < 100 else 'degraded'
        except Exception as e:
            error = str(e)
            latency_ms = self._calc_latency(start_time)
            status = 'unhealthy'

        return RedisHealthResponse(
            status=status,
            latency_ms=latency_ms,
            is_connected=connected,
            error_message=error,
            last_checked_at=datetime.now(timezone.utc),
        )
