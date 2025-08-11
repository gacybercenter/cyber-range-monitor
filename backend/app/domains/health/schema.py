from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from pydantic import Field, PositiveInt
from pydantic import Field, PositiveInt
from typing import Annotated, List

from app.common.schemas.http import ResponseSchema


class DatabaseTableMeta(ResponseSchema):
    """metadata of a database table for health tracking purposes"""

    row_count: Annotated[
        PositiveInt, Field(0, description="The size of the database table in bytes.")
    ] = 0
    table_name: Annotated[
        str, Field(..., description="The name of the database table.")
    ]
    read_time: Annotated[
        float, Field(..., description="The time it took to read all rows.")
    ]


class DatabaseHealthData(ResponseSchema):
    """The response model for a database health check."""

    server_version: Annotated[
        str, Field(..., description="The version of the database server.")
    ]
    driver: Annotated[
        str,
        Field(
            ..., description="Information related to the driver used for the database."
        ),
    ]
    table_meta: Annotated[
        List[DatabaseTableMeta],
        Field(..., description="The metadata for the database tables."),
    ]


class RedisConnectionParams(ResponseSchema):
    host: Annotated[str, Field(..., description="Redis server hostname")]
    port: Annotated[int, Field(..., description="Redis server port")]
    db: Annotated[int, Field(..., description="Redis database number")]
    client_id: Annotated[
        Any | None, Field(None, description="Redis client ID if available")
    ]


RedisHealth = Literal["healthy", "unhealthy", "degraded"]


class RedisHealthResponse(ResponseSchema):
    status: Annotated[
        RedisHealth, Field(..., description="The health status of the Redis server.")
    ]

    latency_ms: Annotated[
        float,
        Field(..., description="The latency of the Redis server in milliseconds."),
    ]

    is_connected: Annotated[
        bool, Field(..., description="Whether the Redis server is connected or not.")
    ]

    error_message: Annotated[
        str | None,
        Field(
            default=None,
            description="The error message if the Redis server is unhealthy.",
        ),
    ]

    last_checked_at: Annotated[
        datetime,
        Field(
            default_factory=lambda: datetime.now(UTC),
            description="The last time the Redis server was checked.",
        ),
    ]


class RedisServerStats(ResponseSchema):
    """The response model for Redis server stats."""

    used_memory: Annotated[
        str, Field(..., description="The amount of memory used by the Redis server.")
    ]

    used_memory_peak: Annotated[
        str, Field(..., description="The peak memory used by the Redis server.")
    ]

    connection_info: Annotated[
        RedisConnectionParams,
        Field(..., description="The connection information for the Redis server."),
    ]

    total_connections: Annotated[
        int,
        Field(..., description="The total number of connections to the Redis server."),
    ]

    uptime_seconds: Annotated[
        int, Field(..., description="The uptime of the Redis server in seconds.")
    ]

    rejected_connections: Annotated[
        int,
        Field(
            ..., description="The number of rejected connections to the Redis server."
        ),
    ]

    connected_clients: Annotated[
        int,
        Field(..., description="The number of connected clients to the Redis server."),
    ]
