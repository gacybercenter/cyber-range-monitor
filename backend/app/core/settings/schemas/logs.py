from typing import Annotated, Literal

from pydantic import Field


from app.core.settings.schemas.base import SettingsMixin

LogLevels = Literal[
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"
]


class LogsConfig(SettingsMixin):
    '''The settings for configuring the logger for the API'''
    db_level: Annotated[LogLevels, Field(
        'INFO',
        description="The log level set to the internal sqlalchemy logger to, (note: it has alot of stdout)."
    )]

    api_level: Annotated[LogLevels, Field(
        'INFO',
        description="The log level set to the internal api logger."
    )]

    service_level: Annotated[LogLevels, Field(
        'INFO',
        description="The log level set to the internal service logger."
    )]

    middleware_level: Annotated[LogLevels, Field(
        'INFO',
        description="The log level set to the internal middleware logger."
    )]

    event_log_level: Annotated[LogLevels, Field(
        'INFO',
        description="The log level set for the EventLog table in the database"
    )]

    allow_file_handler: Annotated[bool, Field(
        False,
        description="Whether to allow the add a file handler to the logger."
    )]
