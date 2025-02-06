from typing import Optional
from .app_config import BaseAppConfig
from functools import lru_cache
from pydantic_settings import SettingsConfigDict


class BuildError(Exception):
    pass


class AppSettings:
    '''Interface for creating / loading the application settings
    supports loading from .env file and keyword arguments and mixin configs.

    Should not be called after application startup; use running_config() instead
    '''
    _instance: 'AppSettings' = None  # type: ignore
    _config: BaseAppConfig = None  # type: ignore

    @classmethod
    def get_instance(cls) -> 'AppSettings':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def from_env(cls, env_path: str = '.env') -> None:
        '''_summary_
        Loads the build configuration from a .env file using the SettingsConfigDict
        and creates a 'BaseAppConfig' instance with the model_config to load the settings

        Keyword Arguments:
            env_path {str} -- _description_ (default: {'.env'})
        '''
        cls.get_instance()

        # this is very cursed, I know
        class _EnvConfig(BaseAppConfig):
            model_config = SettingsConfigDict(
                env_file=env_path,
                env_file_encoding='utf-8',
                extra='ignore',
                frozen=False
            )
        cls._config = _EnvConfig()  # type: ignore
    
    @classmethod
    def from_kwargs(cls, **kwargs) -> None:
        cls.get_instance()
        try:
            cls._config = BaseAppConfig(**kwargs)  # type: ignore
        except Exception as e:
            raise BuildError(
                f'BuildError: Failed to build configuration for arguments likely due to missing required fields\n Details: {
                    e}'
            ) from e

    @classmethod
    def from_mixin(cls, env_path: Optional[str], **kwargs) -> None:
        '''_summary_
        Create the build configuration from a .env file and override
        the settings from env file with the kwargs to create a custom  
        'BaseAppConfig' instance

        Arguments:
            env_path {str} -- _description_
        '''
        cls.get_instance()
        if not env_path:
            env_path = '.env'
            
        cls.from_env(env_path)
        try:
            for setting_key, setting_value in kwargs.items():
                setattr(cls._config, setting_key, setting_value)
        except Exception as e:
            raise BuildError(
                f'BuildError: Failed to build configuration mixin\nDetails: {e}'
            ) from e

    @property
    def config(self) -> BaseAppConfig:
        '''_summary_
        DO NOT USE - use running_config() instead
        Returns:
            BaseAppConfig -- the running config
        '''
        return self._config


@lru_cache()
def running_config() -> BaseAppConfig:
    '''_summary_
    public getter for the build settings of the application
    Returns:
        BaseAppConfig -- the running config
    '''
    instance = AppSettings.get_instance()
    if instance.config is None:
        AppSettings.from_env()
    assert instance.config is not None, 'Failed to build the configuration'
    return instance.config
