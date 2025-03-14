
from typing import Annotated, Literal

from pydantic import Field
from .base import SettingsMixin

AppEnvironment = Literal["container", "local"]
AppMode = Literal["dev", "prod"]


class AppConfig(SettingsMixin):
    """the "app" section of the YAML file"""

    environment: Annotated[AppEnvironment, Field(
        "local",
        description="The environment the app is running in"
    )]

    mode: Annotated[AppMode, Field(
        "dev",
        description="The mode the app is running in (i.e whether to do fastapi run or fastapi dev)",
    )]

    config_label: Annotated[str, Field(
        ...,
        description="The label for the config mapped to the file name (e.g 'dev' -> 'config-dev.yml')",
    )]

    env_file: Annotated[str, Field(
        ".env",
        description="The path to the .env file to load the secrets from."
    )]

    testing: Annotated[bool, Field(False, description="Enable testing mode")]

    debug: Annotated[bool, Field(
        False,
        description="Enables debug mode for fastapi giving tracebacks in 500 errors, DISABLE IN PRODUCTION",
    )]

    min_log_level: Annotated[str, Field(
        "INFO",
        description="Minimum event log level to write to the database"
    )]

    rate_limit: Annotated[str, Field(
        "5/minute",
        description="Number of requests allowed per minute"
    )]

    console_enabled: Annotated[bool, Field(
        True,
        description="Enable the console for the application"
    )]


