
from typing import Annotated, Literal

from pydantic import Field
from .base import SettingsMixin

AppEnvironment = Literal["container", "local"]
AppMode = Literal["dev", "prod"]

LogLevel = Literal[
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"
]


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

    testing: Annotated[bool, Field(
        False,
        description="Enables testing mode, note if not enabled during testing errors may occur"
    )]

    debug: Annotated[bool, Field(
        False,
        description="Enables debug mode for fastapi resulting in tracebacks in responses, DISABLE IN PRODUCTION",
    )]

    rate_limit: Annotated[str, Field(
        "5/minute",
        description="Number of requests allowed per minute"
    )]

    console_enabled: Annotated[bool, Field(
        True,
        description="Enables the console for the application (reccomended for local development only)"
    )]

    allow_documentation: Annotated[bool, Field(
        True,
        description="Specifies whether the SwaggerUI documentation route should be included or not. DISABLE IN PRODUCTION"
    )]
