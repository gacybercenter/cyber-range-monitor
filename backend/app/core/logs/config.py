
from typing import Annotated, Any, Dict, Generator, List
from pydantic import Field

from common.yml_config.settings import YAMLSettings, get_app_config_file
from app.common.types import LogLevels


SECTION_NAME = "logs"




class LogLevelsConfig(YAMLSettings):
    uvicorn: Annotated[LogLevels, Field(
        default='DEBUG',
        description='The log level for the uvicorn logger'
    )]

    stdout: Annotated[LogLevels, Field(
        default='INFO',
        description='The log level for the stdout logger'
    )]

    file: Annotated[LogLevels, Field(
        default='INFO',
        description='The log level for the file logger'
    )]


class LogSettings(YAMLSettings):
    '''The log settings for the application.'''
    use_rich: Annotated[bool, Field(
        default=True,
        description='Whether to use rich logging or not for colorized / developer friendly output.'
    )]

    max_file_mb: Annotated[int, Field(
        default=5,
        description='The max size of the log file in MB before it is rotated.'
    )]

    log_levels: Annotated[LogLevelsConfig, Field(
        ...,
        description='The log levels for the different loggers.'
    )]

    websocket_enabled: Annotated[bool, Field(
        default=True,
        description='Whether to enable websocket logging or not.'
    )]

    websocket_loggers: Annotated[List[str], Field(
        default=['app'],
        description='The loggers to enable websocket logging for.'
    )]

    uvicorn_audit: Annotated[bool, Field(
        default=False,
        description='Whether to enable uvicorn access logging or not.'
    )]

    @property
    def file_size(self) -> int:
        '''the max file size in bytes.'''
        return self.max_file_mb * 1024 * 1024


log_settings = LogSettings.create(
    section_name=SECTION_NAME,
    file_cache=get_app_config_file()
)
