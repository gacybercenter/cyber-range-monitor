import os
from typing import Annotated, Literal

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings

JournalModeTypes = Literal[
    'DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF'
]


class DatabaseSettings(BaseSettings):
    '''the "database" section of the YAML file'''
    url: Annotated[str,  Field(
        'sqlite+aiosqlite:///instance/app.db', description='The URL for the database connection'
    )]
    sqlalchemy_echo: Annotated[bool, Field(
        True, description='Enable SQLAlchemy queries to be printed to stdout'
    )]
    timeout: Annotated[PositiveInt, Field(
        30, description='Timeout for SQLite connection in seconds'
    )]
    busy_timeout: Annotated[PositiveInt, Field(
        5000, description='Timeout for SQLite busy handler'
    )]
    journal_mode: Annotated[JournalModeTypes, Field(
        'WAL', description='Journal mode for SQLite'
    )]

    def resolve_url_dir(self) -> str:
        '''Returns the directory path for the SQLite database URL
        Returns:
            str: directory path for the SQLite database URL
        '''
        db_path = self.url.split('///')[1]
        return os.path.dirname(db_path)

    def pragmas(self) -> dict:
        '''Returns the dictionary of pragmas for the SQLite database
        Returns:
            dict: dictionary of pragmas
        '''
        return {
            "journal_mode": self.journal_mode,
            "foreign_keys": "ON",
            "busy_timeout": self.busy_timeout
        }

    def connect_args(self) -> dict:
        '''Returns the dictionary of connect arguments for the SQLite database
        Returns:
            dict: dictionary of connect arguments
        '''
        return {
            "check_same_thread": False,
            "timeout": self.timeout,
        }

    def __repr__(self) -> str:
        return f"DatabaseSettings(url={self.url}, sqlalchemy_echo={self.sqlalchemy_echo}, timeout={self.timeout}, busy_timeout={self.busy_timeout}, journal_mode={self.journal_mode})"
