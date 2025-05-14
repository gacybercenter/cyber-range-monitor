

from typing import Annotated

from pydantic import Field

from app.common.yml_config import YAMLSettings, get_app_config_file

SECTION_NAME = 'app'


class AppSettings(YAMLSettings):
    '''The non-sensitive build settings for the application'''

    label: Annotated[str, Field(
        ...,
        description="The label for the config mapped to the file name (e.g 'dev' -> 'config-dev.yml')",
    )]

    debug: Annotated[bool, Field(
        False,
        description="Enables debug mode for fastapi resulting in tracebacks in responses, DISABLE IN PRODUCTION",
    )]

    env_file: Annotated[str, Field(
        ".env",
        description="The path to the .env file to load the secrets from."
    )]

    testing: Annotated[bool, Field(
        False,
        description="Enables testing mode, note if not enabled during testing errors may occur"
    )]

    allow_documentation: Annotated[bool, Field(
        True,
        description="Specifies whether the SwaggerUI documentation route should be included or not. DISABLE IN PRODUCTION"
    )]


app_settings = AppSettings.create(
    section_name=SECTION_NAME
)
