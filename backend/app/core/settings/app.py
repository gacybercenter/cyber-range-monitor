from typing import Annotated

from pydantic import Field

from .base import TomlSettings


class DocsConfig(TomlSettings):
    '''
    Settings for the documentation routes.

    Parameters
    ----------
    TomlSettings : _type_
    '''
    docs_url: Annotated[
        str,
        Field(
            description='The URL for the SwaggerUI documentation route.',
        ),
    ] = '/docs'

    redoc_url: Annotated[
        str,
        Field(
            description='The URL for the ReDoc documentation route.',
        ),
    ] = '/redoc'

    openapi_url: Annotated[
        str,
        Field(
            description='The URL for the OpenAPI schema.',
        ),
    ] = '/openapi.json'

    allow_docs: Annotated[
        bool,
        Field(
            description='Whether to allow the documentation routes.',
        ),
    ] = True


class OpenAPIConfig(TomlSettings):
    '''
    Whats displayed in the OpenAPI documentation.

    Parameters
    ----------
    TomlSettings : _type_
    '''
    title: str = Field(
        'range-monitor-api',
        description='The name of the application, used in the OpenAPI documentation and other places.',
    )

    description: str = Field(
        'A RESTful API for the Cyber Range Monitor',
        description='The description of the application, used in the OpenAPI documentation.',
    )

    version: Annotated[
        str,
        Field(
            description='The version of the app, used in the OpenAPI documentation.',
        ),
    ] = '0.1.0'

    summary: Annotated[
        str,
        Field(
            description='A short summary, used in the OpenAPI documentation / routes',
        )
    ] = 'The backend of the Range Monitor.'


class AppConfig(TomlSettings):
    '''
    Settings needed for the application to run or are fastapi specific.
    '''
    label: Annotated[
        str,
        Field(description="The label for the config mapped (e.g 'dev' -> 'config-dev.yml')"),
    ]

    debug: Annotated[
        bool,
        Field(
            description='Enables debug mode, DISABLE IN PRODUCTION',
        ),
    ] = False

    env_file: Annotated[
        str,
        Field(
            description='The path to the environment file, used to load environment variables.',
        ),
    ] = '.env'

    testing: Annotated[
        bool,
        Field(
            description='Whether the application is running in testing mode.',
        ),
    ] = False

    openapi: OpenAPIConfig
    docs: DocsConfig
