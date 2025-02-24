import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict



def settings_config(env_prefix: str) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_file=f'.{os.getenv('APP_ENV', 'dev')}.env',
        env_file_encoding='utf-8',
        env_prefix=env_prefix,
        extra='ignore'
    )


class AppConfig(BaseSettings):
    DESCRIPTION: str = Field(
        'An opensource API for monitoring the cloud environments in the Georgia Cyber Range',
        description='Description of the application'
    )
    TITLE: str = 'Range Monitor v2 - API'
    USE_DOCS: bool = Field(
        True,
        description='Use the FastAPI docs'
    )
    ENABLE_LOGGING: bool = Field(
        True,
        description='Enable logging'
    )
    ENABLE_CONSOLE: bool = Field(
        True,
        description='Enable the console for the application'
    )
    model_config: SettingsConfigDict = settings_config('APP_')
    

    