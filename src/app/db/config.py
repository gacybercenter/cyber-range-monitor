from pydantic import Field
from pydantic_settings import BaseSettings

from app.config import settings_config

class DatabaseConfig(BaseSettings):
    URL: str = Field(
        ...,
        description='The URL to the database (e.g sqlite+aiosqlite:///./instance/app.db)'
    )
    ECHO: bool = Field(
        False,
        description='Echo the database queries to the console'
    )
    USE_PRAGMAS: bool = Field(
        True,
        description='Use the pragmas for the database'
    )
    model_config = settings_config(env_prefix='DB_')
    