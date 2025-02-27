from .yml_source import YamlBaseSettings
from .app import ApiConfig, ApiDocsSettings
from .database import DatabaseSettings
from .redis import RedisSettings
from .sessions import SessionSettings
from .pyproject_info import PyProjectInfo

# package represents configs that are "static" or are not
# dynamic such as the pyproject.toml and config.yml files

static_config_map = {
    'app': ApiConfig,
    'docs': ApiDocsSettings,
    'database': DatabaseSettings,
    'redis': RedisSettings,
    'sessions': SessionSettings,
    'pyproject': PyProjectInfo
}


class SettingsYml(YamlBaseSettings):
    '''represents all of the combined settings from the config.yml file'''
    api_config: ApiConfig
    database: DatabaseSettings
    redis: RedisSettings
    sessions: SessionSettings
