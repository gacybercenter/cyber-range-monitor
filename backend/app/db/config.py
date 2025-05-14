
from typing import Annotated, Literal, Self

from app.common.yml_config import YAMLSettings

from pydantic import Field


class EngineSettings(YAMLSettings):
    """SQLite settings for the ORM plugin."""
    pool_recycle: Annotated[int, Field(
        default=3600,
        description="The number of seconds to recycle the connection pool."
    )] = 3600
    pool_timeout: Annotated[int, Field(
        default=30,
        description="The number of seconds to wait for a connection from the pool."
    )] = 30
    pool_size: Annotated[int, Field(
        default=10,
        description="The number of connections to keep in the pool."
    )] = 10
    max_overflow: Annotated[int, Field(
        default=10,
        description="The maximum number of connections to create beyond the pool size."
    )] = 10
    pool_use_lifo: Annotated[bool, Field(
        default=False,
        description="Whether to use LIFO instead of FIFO for the connection pool."
    )] = False

    pool_pre_ping: Literal[True] = True
    future: Literal[True] = True
    pool_pre_ping: Literal[True] = True


class DatabaseSettings(YAMLSettings):

    engine: Annotated[EngineSettings, Field(
        EngineSettings(),
        description="The engine settings for sqlalchemy."
    )]

    file_name: Annotated[str, Field(
        default=":memory:",
        description="The SQLite database file path."
    )]

    timeout: Annotated[int, Field(
        default=30,
        description="The number of seconds to wait for a connection before timing out."
    )]

    directory: Annotated[str, Field(
        default="instance",
        description="The directory where the SQLite database file is located."
    )]

    echo: Annotated[bool, Field(
        default=False,
        description="Whether to echo SQL statements."
    )]

    run_seed: Annotated[bool, Field(
        default=False,
        description="Whether to run the seed file on startup."
    )]

    def database(self) -> str:
        """Returns the database URL."""
        return f"{self.directory}/{self.file_name}"


SECTION_NAME = 'database'
db_settings = DatabaseSettings.create(
    section_name=SECTION_NAME,
)
