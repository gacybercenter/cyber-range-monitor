from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.core.settings import TomlLoader, TomlSettings

LoguruLevels = Literal[
    'TRACE',
    'DEBUG',
    'INFO',
    'SUCCESS',
    'WARNING',
    'ERROR',
    'CRITICAL',
]

LoguruCompression = Literal['zip', 'tar', 'gz', 'bz2', 'xz', 'none']


class JsonLoggerSink(BaseModel):
    name: Annotated[
        str,
        Field(
            description='The name of the logger and sub directory directory to store files',
        ),
    ]
    level: Annotated[
        LoguruLevels,
        Field(
            description='The minimum level to log to this logger',
        ),
    ] = 'INFO'


class LoggerSettings(TomlSettings):
    json_loggers: Annotated[
        list[JsonLoggerSink],
        Field(description='List of JSON loggers to be created')
    ]

    stdout_level: Annotated[
        LoguruLevels,
        Field(description='The minimum level to log to stdout'),
    ] = 'INFO'

    directory: Annotated[
        str,
        Field(
            description='The directory to store log files',
            default='logs',
        )
    ] = 'logs'

    rotation_mb: Annotated[
        int,
        Field(
           description='The size in megabytes to rotate log files',
           ge=1,
           le=1000,
        )
    ] = 10

    retention_days: Annotated[
        int,
        Field(
            description='The number of days to retain log files',
            ge=1,
            le=365,
        )
    ] = 7

    compression: Annotated[
        LoguruCompression,
        Field(description='The compression method to use for rotated log files'),
    ] = 'zip'

    @property
    def stdout_format(self) -> str:
        return (
            '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
            '<level>{level: <8}</level> | '
            'cid=<cyan>{extra[correlation_id]}</cyan> | '
            '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
            '<level>{message}</level>'
        )


log_settings: LoggerSettings = TomlLoader.load(
    settings_class=LoggerSettings,
    section_name='logging',
)
