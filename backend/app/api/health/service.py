

from datetime import datetime, timezone
import time
from typing import Any
import aiosqlite
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MODEL_LIST
from app.redis import redis_client


from .schema import (
    DatabaseHealthData,
    DatabaseTableMeta,
    RedisConnectionParams,
    RedisHealthResponse,
    RedisServerStats
)


class DatabaseHealthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_server_version(self) -> Any:
        """Returns the server version of the database."""
        result = await self.db.execute(text("SELECT sqlite_version()"))
        return result.scalar()

    async def get_model_metadata(self, model: Any) -> DatabaseTableMeta:
        '''gets metadata about a database model including the number of rows
        the time it took to read and the name of the table.

        Args:
            model (Any): _the model to read from_

        Returns:
            DatabaseTableMeta: _the meta data about the database model_
        '''
        table_name = model.__tablename__
        read_start = time.perf_counter()
        statement = select(func.count()).select_from(model)  # type: ignore
        result = await self.db.execute(statement)
        row_count = result.scalar_one()
        read_time = time.perf_counter() - read_start
        return DatabaseTableMeta(
            table_name=table_name,
            row_count=row_count,
            read_time=read_time
        )

    async def get_db_info(self) -> DatabaseHealthData:
        model_data = [
            await self.get_model_metadata(model)
            for model in MODEL_LIST
        ]
        server_version = await self.get_server_version()
        driver_info = aiosqlite.__version__
        return DatabaseHealthData(
            server_version=server_version,
            driver=f'SQLite {driver_info}',
            table_meta=model_data
        )


class RedisHealthService:
    '''_Service class for redis health check_'''
    def __init__(self) -> None:
        self.client = redis_client

    def get_connection_params(self) -> RedisConnectionParams:
        """Returns the connection parameters for the Redis client."""
        client_id = None
        try:
            client_id = self.client.client_id()
        except Exception:
            pass
        return RedisConnectionParams(
            host=self.client.host,
            port=self.client.port,
            db=self.client.db,
            client_id=client_id
        )

    async def get_server_stats(self) -> RedisServerStats:
        '''gets general health related information about the Redis server.

        Returns:
            RedisServerStats: _the server stats_
        '''
        redis_info = await self.client.info()

        uptime_seconds = redis_info.get('uptime_in_seconds', 0)
        used_memory = redis_info.get('used_memory_human', '0B')
        used_memory_peak = redis_info.get('used_memory_peak_human', '0B')
        connected_clients = int(redis_info.get('connected_clients', 0))

        connection_info = self.get_connection_params()
        total_connections = int(redis_info.get(
            'total_connections_received', 0))
        connected_clients = int(redis_info.get('connected_clients', 0))

        rejected_connections = int(redis_info.get('rejected_connections', 0))
        return RedisServerStats(
            used_memory=used_memory,
            used_memory_peak=used_memory_peak,
            uptime_seconds=uptime_seconds,
            total_connections=total_connections,
            connected_clients=connected_clients,
            rejected_connections=rejected_connections,
            connection_info=connection_info
        )

    async def get_redis_health(self) -> RedisHealthResponse:
        '''** Check Redis Health ***
        gets health related information about the redis client including the
        latency, connection status, and error message if any.

        Returns:
            RedisHealthResponse: _the health response schema_
        '''

        start_time = time.perf_counter()
        connected = False
        error = None
        try:
            connected = await self.client.ping()
            latency_ms = (time.perf_counter() - start_time) * 1000
            status = 'healthy' if latency_ms < 100 else 'degraded'
        except Exception as e:
            error = str(e)
            latency_ms = (time.perf_counter() - start_time) * 1000
            status = 'unhealthy'

        return RedisHealthResponse(
            status=status,
            latency_ms=latency_ms,
            is_connected=connected,
            error_message=error,
            last_checked_at=datetime.now(timezone.utc)
        )
