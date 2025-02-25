

import os
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

JournalTypes = Literal['DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF']
DATABASE_ENV_PREFIX = 'DATABASE_'


class DatabaseConfig(BaseSettings):
    '''The SQLite Database configuration settings'''
    URL: str = Field(
        ...,
        description='URL for the database connection'
    )
    ECHO: bool = Field(True, description='Echo Database SQL queries to stdout')
    BUSY_TIMEOUT: int = Field(
        5000,
        description='Timeout for SQLite busy handler'
    )
    JOURNAL_MODE: JournalTypes = Field(
        'WAL',
        description='Journal mode for SQLite'
    )
    TIMEOUT: int = Field(
        30,
        description='Timeout for SQLite connection in seconds'
    )

    def resolve_url_dir(self) -> str:
        '''Returns the directory path for the SQLite database URL
        '''
        db_path = self.URL.split('///')[1]
        return os.path.dirname(db_path)

    def pragmas(self) -> dict:
        '''Returns the dictionary of pragmas for the SQLite database

        Returns:
            dict: dictionary of pragmas
        '''
        return {
            "journal_mode": self.JOURNAL_MODE,
            "foreign_keys": "ON",
            "busy_timeout": self.BUSY_TIMEOUT
        }

    def connect_args(self) -> dict:
        '''Returns the dictionary of connect arguments for the SQLite database

        Returns:
            dict: dictionary of connect arguments
        '''
        return {
            "check_same_thread": False,
            "timeout": self.TIMEOUT,
        }

    @field_validator('URL', mode='before')
    @classmethod
    def check_url(cls, value: str) -> str:
        '''Validates the URL field to ensure it is a valid SQLite URL

        Args:
            value (str): The URL to validate

        Returns:
            str: The validated URL
        '''
        if not value.startswith('sqlite+aiosqlite:///'):
            raise ValueError(
                'DatabaseConfig: The Database URL must start with sqlite+aiosqlite:///')
        return value
