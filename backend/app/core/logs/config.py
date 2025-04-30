
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

    log_level: Annotated[LogLevels, Field(
        ...,
        description='The root logger log level'
    )]

    stdout: Annotated[bool, Field(
        ...,
        description='whether to use rich handlers or not.'
    )]


log_settings = LoggingSettings.load(
    get_yml_file_section(SECTION_NAME)
)
