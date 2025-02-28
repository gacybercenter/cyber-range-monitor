from pathlib import Path
from typing import Annotated

from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings


class ApiDocsSettings(BaseSettings):
    '''The "api_docs" section of the YAML file'''
    enable: Annotated[bool, Field(
        True, description='Enable the API documentation'
    )]
    swagger: Annotated[str, Field(
        '/docs', description='The URL for the Swagger UI'
    )]
    redoc: Annotated[str,  Field(
        '/redoc', description='The URL for the ReDoc UI'
    )]
    openapi: Annotated[str, Field(
        '/openapi.json', description='The URL for the OpenAPI JSON'
    )]

    def register_docs(self, app: FastAPI) -> None:
        '''adds the API documentation to the app'''
        app.redoc_url = self.redoc
        app.openapi_url = self.openapi
        app.docs_url = self.swagger


class ApiConfig(BaseSettings):
    '''the "api_config" section of the YAML file
    '''
    environment: Annotated[str, Field(
        'dev', description='The environment the app is running in'
    )]
    env_file: Annotated[str, Field(
        '.env', description='The path to the .env file to load the secrets from.'
    )]
    testing: Annotated[bool, Field(
        False, description='Enable testing mode'
    )]
    debug: Annotated[bool, Field(
        False, description='Enables debug mode for fastapi giving tracebacks in 500 errors, DISABLE IN PRODUCTION'
    )]
    min_log_level: Annotated[str, Field(
        'INFO', description='Minimum event log level to write to the database'
    )]
    use_security_headers: Annotated[bool, Field(
        False,
        description=(
            'WARNING: this breaks SwaggerUI '
            'Whether or not to use the Security Header middleware which wraps all requests with security headers'
        )
    )]
    rate_limit: Annotated[str, Field(
        '5/minute', description='Number of requests allowed per minute'
    )]
    console_enabled: Annotated[bool, Field(
        True, description='Enable the console for the application'
    )]


    def secrets_file_path(self) -> Path:
        '''returns the path to the .env file'''
        return Path(self.env_file).resolve()