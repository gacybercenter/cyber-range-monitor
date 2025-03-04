from pydantic_settings import BaseSettings

from .app import ApiConfig, ApiDocsSettings
from .database import DatabaseSettings
from .pyproject_info import PyProjectInfo
from .redis import RedisSettings
from .sessions import SessionSettings
from .yml_source import YamlBaseSettings

# package represents configs that are "static" or are not
# dynamic such as the pyproject.toml and config.yml files

static_config_map: dict[str, type[BaseSettings]] = {
    "app": ApiConfig,
    "docs": ApiDocsSettings,
    "database": DatabaseSettings,
    "redis": RedisSettings,
    "sessions": SessionSettings,
    "pyproject": PyProjectInfo,
}


class SettingsYml(YamlBaseSettings):
    """represents all of the combined settings from the config.yml file"""

    app: ApiConfig
    database: DatabaseSettings
    redis: RedisSettings
    sessions: SessionSettings
    documentation: ApiDocsSettings
