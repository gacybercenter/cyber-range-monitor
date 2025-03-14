from typing import Annotated, Literal
from pathlib import Path

from pydantic import Field, NegativeInt, PositiveInt, field_validator
import sqlalchemy

from .base import SettingsMixin


NON_ASYNC_URL_ERROR = (
    "Sync SQLite is not supported, use an aiosqlite URL instead "
    "(e.g 'sqlite+aiosqlite:///instance/app.db')"
)
UNMOUNTABLE_URL_ERROR = (
    "Invalid database URL, there should be a directory in the URL "
    " so a SQLite .db file volume can be mounted for the docker container "
    "(e.g) sqlite+aiosqlite:///instance/app.db -> 'instance' is the directory"
)

JournalModeTypes = Literal[
    "DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"
]

SynchronousTypes = Literal["NORMAL", "FULL", "OFF"]


def bad_db_url(reason: str, url: str) -> ValueError:
    raise ValueError(
        f'InvalidDatabaseURL: "{url}" is not an acceptable database url.\n\t{reason}')


class DatabaseConfig(SettingsMixin):
    """the "database" section of the YAML file"""

    url: Annotated[str, Field(
        "sqlite+aiosqlite:///instance/app.db",
        description="The URL for the database connection"
    )]
    sqlalchemy_echo: Annotated[bool, Field(
        True,
        description="Enable SQLAlchemy queries to be printed to stdout, useful for debugging"
    )] = True

    timeout: Annotated[PositiveInt, Field(
        30,
        description="The seconds before a connection attempt should timeout."
    )]
    journal_mode: Annotated[JournalModeTypes, Field(
        "WAL",
        description="Journal mode for SQLite, WAL is reccomended for production environments and DELETE is reccomended for testing environments"
    )] = "WAL"
    synchronous: Annotated[SynchronousTypes, Field(
        "NORMAL",
        description="Synchronous mode for SQLite, NORMAL is reccomended and optimized for async."
    )] = "NORMAL"
    cache_size: Annotated[NegativeInt, Field(
        -64000,
        description="The cache size for SQLite in kilobytes, good for websockets"
    )] = -64000

    @field_validator("url", mode="after")
    @classmethod
    def validate_url(cls, value: str) -> str:
        '''ensures the database URL supports async operations and is can be mounted 
        in a docker container for data persistence. The URL must start with 'sqlite+aiosqlite:///'
        Arguments:
            value {str} -- the database URL to validate
        Returns:
            str -- the validated database URL
        '''
        if not value.startswith("sqlite+aiosqlite:///"):
            bad_db_url(NON_ASYNC_URL_ERROR, value)
        url_tokens = value.split("///")
        if len(url_tokens) < 2:
            bad_db_url(UNMOUNTABLE_URL_ERROR, value)
        return value

    def url_dirname(self) -> Path:
        """Returns the directory path for the SQLite database URL
        Returns:
            str: directory path for the SQLite database URL
        """
        url_tokens = self.url.split("///")
        if len(url_tokens) < 2:
            bad_db_url(UNMOUNTABLE_URL_ERROR, self.url)
        db_path = url_tokens[1]
        return Path(db_path).parent

    def get_pragmas(self) -> dict:
        '''Returns the dictionary of pragmas for the SQLite database
        Returns:
            dict -- the dictionary of the pragma name and the set value
        '''
        return {
            "journal_mode": self.journal_mode,
            "synchronous": self.synchronous,
            "cache_size": self.cache_size,
            "temp_store": "memory",
            "foreign_keys": 1,
        }

    def connect_args(self) -> dict:
        """Returns the dictionary of connect arguments for the SQLite database
        Returns:
            dict: dictionary of connect arguments
        """

        return {
            "check_same_thread": False,
            "timeout": self.timeout
        }
