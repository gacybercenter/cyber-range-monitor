from typing import Annotated
from pydantic import Field

from app.common.types import LevelNumber, LevelNames
from app.common.yml_config import YAMLSettings


SECTION_NAME = "logs"


class LevelNumberFilters(YAMLSettings):
    std_level: Annotated[
        LevelNumber,
        Field(default=10, description="The default log level for all loggers"),
    ] = 10

    file_level: Annotated[
        LevelNumber, Field(default=10, description="The log level for the file logger")
    ] = 10


class LevelNameOptions(YAMLSettings):
    uvicorn_level: Annotated[
        LevelNames,
        Field(default="INFO", description="The log level for the uvicorn logger"),
    ]

    std_level: Annotated[
        LevelNames,
        Field(default="DEBUG", description="The log level for the standard logger"),
    ]

    file_level: Annotated[
        LevelNames,
        Field(default="WARNING", description="The log level for the file logger"),
    ]


class LogSettings(YAMLSettings):
    """The log settings for the application."""

    use_colors: Annotated[
        bool,
        Field(
            default=True,
            description="Whether to use rich logging or not for colorized / developer friendly output.",
        ),
    ]

    rotation_megabytes: Annotated[
        int,
        Field(
            default=5,
            description="The max size of the log file in MB before it is rotated.",
        ),
    ]

    level_name: Annotated[
        LevelNameOptions,
        Field(..., description="The log levels for the different loggers."),
    ]

    level_filters: Annotated[
        LevelNumberFilters,
        Field(
            default=LevelNumberFilters(),
            description="The log levels for the different loggers.",
        ),
    ]

    uvicorn_audit: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to enable uvicorn access logging or not.",
        ),
    ]

    # websocket_logger_names: Annotated[list[str], Field(
    #     default=[],
    #     description='The names of the loggers to use for the websocket logger.'
    # )]


log_settings = LogSettings.create(section_name=SECTION_NAME)
