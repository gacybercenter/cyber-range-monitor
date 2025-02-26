from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings


LogTypes = Literal['INFO', 'WARNING', 'ERROR', 'CRITICAL']


class AppConfig(BaseSettings):
    '''The main configuration for the application
    '''
    ENVIRONMENT: str = Field(
        'dev',
        description='IMPORTANT: The environment the app is running in'
    )
    TESTING: bool = Field(
        False,
        description='Enable testing mode'
    )
    DEBUG: bool = Field(
        False,
        description='Enables debug mode for fastapi giving tracebacks in 500 errors, DISABLE IN PRODUCTION'
    )
    MIN_LOG_LEVEL: LogTypes = Field(
        'INFO',
        description='Minimum event log level to write to the database'
    )
    USE_SECURITY_HEADERS: bool = Field(
        False,
        description='WARNING: this breaks SwaggerUI Whether or not to use the Security Header middleware which wraps all requests with security headers'
    )
    ALLOW_DOCUMENTATION: bool = Field(
        True,
        description='Allow the documentation routes from OpenAPI and Redoc DISABLE IN PRODUCTION'
    )
    RATE_LIMIT: str = Field(
        '5/minute',
        description='Number of requests allowed per minute'
    )
    ENABLE_CONSOLE: bool = Field(
        True,
        description='Enable the console for the application'
    )
    
    def api_doc_urls(self) -> dict[str, str]:
        '''Returns the urls for the API documentation'''
        return {
            'swagger': '/docs',
            'openapi': '/openapi.json',
            'redoc': '/redoc'
        }
