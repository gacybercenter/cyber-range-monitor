import os
from typing import Annotated, Literal
from pydantic_settings import BaseSettings
from pydantic import Field, PositiveInt, field_validator

JournalModeTypes = Literal[
    'DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF'
]


class DatabaseSettings(BaseSettings):
    '''the "database" section of the YAML file'''
    url: Annotated[str,  Field(
        ..., description='The URL for the database connection'
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

    @field_validator('url', mode='before')
    @classmethod
    def check_url(cls, v: str) -> str:
        '''Validates the URL for the database connection
        '''
        if not v.startswith('sqlite+aiosqlite:///'):
            raise ValueError(
                'InvalidSettingsError: URL must start with "sqlite+aiosqlite:///"'
            )
        return v

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
