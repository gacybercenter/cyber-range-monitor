
from typing import Annotated, Literal
from pydantic import Field

from app.common.yml_settings import YMLBuildSettings, get_yml_file_section


SECTION_NAME = "logs"

LogLevels = Literal[
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG"
]


class LoggingSettings(YMLBuildSettings):
    
    stdout_level: Annotated[LogLevels, Field(
        'DEBUG',
        description="The log level for the console logger."
    )] 
    
    stdout: Annotated[bool, Field(
        default=True,
        description="Whether to use stdout logging."
    )]
    
    use_rich: Annotated[bool, Field(
        default=True,
        description="Whether to use rich logging."
    )] 
    
    file_log_level: Annotated[LogLevels, Field(
        'INFO',
        description="The log level for the file logger."
    )]



log_settings = LoggingSettings.load(
    get_yml_file_section(SECTION_NAME)
)


