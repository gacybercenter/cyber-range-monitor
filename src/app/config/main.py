import os
from functools import lru_cache
from .base import AppConfig
from .prod import ProductionConfig
from .dev import DevConfig


class BuildError(Exception):
    pass


class AppSettings:
    '''Interface for creating / loading the application settings
    supports loading from .env file and keyword arguments and mixin configs.

    Should not be called after application startup; use running_config() instead
    '''
    _instance: 'AppSettings' = None  # type: ignore
    _config: AppConfig = None  # type: ignore

    @classmethod
    def get_instance(cls) -> 'AppSettings':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def load_config(cls) -> None:
        '''Loads the build configuration from a .env file using the SettingsConfigDict
        and creates a 'AppConfig' instance with the model_config to load the settings

        Keyword Arguments:
            env_path {str} -- _description_ (default: {'.env'})
        '''
        cls.get_instance()
        env = os.getenv('APP_ENV')
        if env == 'prod':
            cls._config = ProductionConfig()  # type: ignore
        elif env == 'dev':
            cls._config = DevConfig() # type: ignore
        else: 
            raise BuildError('Unknown "API_ENV" environment set the APP_ENV environment variable to "prod" or "dev"')
        
        
        
    @classmethod
    def test_config(cls, cli_config: dict) -> None:
        try:
            cls.get_instance()
            AppConfig(**cli_config)
        except Exception as e:
            raise BuildError(f'Failed to build the configuration: {e}')
        
    
    @property
    def config(self) -> AppConfig:
        '''_summary_
        DO NOT USE - use running_config() instead
        Returns:
            AppConfig -- the running config
        '''
        return self._config



@lru_cache()
def running_config() -> AppConfig:
    '''_summary_
    public getter for the build settings of the application
    Returns:
        AppConfig -- the running config
    '''
    instance = AppSettings.get_instance()
    if instance.config is None:
        AppSettings.load_config()
    assert instance.config is not None, 'Failed to build the configuration'
    return instance.config
