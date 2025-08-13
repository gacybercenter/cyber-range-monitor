from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field, PositiveInt

from .interface import ResponseSchema


class DatabaseTableMeta(ResponseSchema):
    """metadata of a database table for health tracking purposes"""

    row_count: PositiveInt = Field(
        0, description='The size of the database table in bytes.'
    )
    table_name: str = Field(..., description='The name of the database table.')
    read_time: float = Field(..., description='The time it took to read all rows.')


class DatabaseHealthData(ResponseSchema):
    """The response model for a database health check."""

    server_version: str = Field(..., description='The version of the database server.')
    driver: str = Field(
        ..., description='Information related to the driver used for the database.'
    )
    table_meta: list[DatabaseTableMeta] = Field(
        ..., description='The metadata for the database tables.'
    )


class RedisConnectionParams(ResponseSchema):
    host: str = Field(..., description='Redis server hostname')
    port: int = Field(..., description='Redis server port')
    db: int = Field(..., description='Redis database number')
    client_id: Any | None = Field(None, description='Redis client ID if available')


RedisHealth = Literal['healthy', 'unhealthy', 'degraded']


class RedisHealthResponse(ResponseSchema):
    status: RedisHealth = Field(
        ..., description='The health status of the Redis server.'
    )
    latency_ms: float = Field(
        ..., description='The latency of the Redis server in milliseconds.'
    )
    is_connected: bool = Field(
        ..., description='Whether the Redis server is connected or not.'
    )
    error_message: str | None = Field(
        default=None,
        description='The error message if the Redis server is unhealthy.',
    )
    last_checked_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description='The last time the Redis server was checked.',
    )


class RedisServerStats(ResponseSchema):
    """The response model for Redis server stats."""

    used_memory: str = Field(
        ..., description='The amount of memory used by the Redis server.'
    )
    used_memory_peak: str = Field(
        ..., description='The peak memory used by the Redis server.'
    )
    connection_info: RedisConnectionParams = Field(
        ..., description='The connection information for the Redis server.'
    )
    total_connections: int = Field(
        ..., description='The total number of connections to the Redis server.'
    )
    uptime_seconds: int = Field(
        ..., description='The uptime of the Redis server in seconds.'
    )
    rejected_connections: int = Field(
        ..., description='The number of rejected connections to the Redis server.'
    )
    connected_clients: int = Field(
        ..., description='The number of connected clients to the Redis server.'
    )
