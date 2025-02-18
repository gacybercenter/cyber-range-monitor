import os
from functools import lru_cache

from app.common import console
from .base import AppConfig
from .presets import DevConfig, ProdConfig, create_config_mixin


class Settings:
    '''Interface for creating / loading the application settings
    supports loading from .env file and keyword arguments and mixin configs.

    Should not be called after application startup; use running_config() instead
    '''
    _instance: 'Settings' = None  # type: ignore
    _config: AppConfig = None  # type: ignore

    @classmethod
    def get_instance(cls) -> 'Settings':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def load(cls) -> None:
        '''Uses the APP_ENV environment variable to determine which configuration to use
        for the build settings

        Note:
            - the APP_ENV is used to determine the .env file to read from (.<APP_ENV>.env) 
            - if APP_ENV is not set it will default to 'dev' and will recieve 
            a warning 

        Examples:
            APP_ENV=prod -> .prod.env
            APP_ENV=dev -> .dev.env

        Returns:
            AppConfig -- the configuration to use for the build settings
        '''
        cls.get_instance()
        current_env = os.getenv('APP_ENV')
        # dev config is not set because it'll load the .env file on initilization
        if not current_env:
            Settings.env_not_set()
            cls._config = DevConfig()  # type: ignore
            return

        if current_env == 'prod':
            cls._config = ProdConfig()  # type: ignore
            return

        if current_env == 'dev':
            cls._config = DevConfig()  # type: ignore
            return
        try:
            cls._config = create_config_mixin(current_env)
        except FileNotFoundError:
            Settings.unknown_env(current_env)
            cls._config = DevConfig()  # type: ignore

    @classmethod
    def test_config(cls, cli_config: dict) -> None:
        try:
            cls.get_instance()
            AppConfig(**cli_config)
        except Exception as e:
            raise Exception(f'Failed to build the configuration: {e}') from e

    @property
    def config(self) -> AppConfig:
        '''DO NOT USE - use running_config() instead
        Returns:
            AppConfig -- the running config
        '''
        return self._config

    @staticmethod
    def unknown_env(current_env: str) -> None:
        console.print(
            f'[bold red] !!! WARNING !!![/bold red]: '
            f'[red]Note:[/red]: [italic] The APP_ENV environment variable is set to "{current_env}"[/italic]'
            f'[bold blue] but no .{current_env}.env file was found...[/bold blue]'
            '[italic yellow]using the Development Config as a fallback...[/italic yellow]'
        )

    @staticmethod
    def env_not_set() -> None:
        console.print(
            '[bold red]!!! WARNING !!![/bold red]: \n'
            '[red]Note: [/red] [italic]The "APP_ENV" environment variable was not set at runtime\n[/italic]'
            '[italic white]\nTo no longer see this message, set the APP_ENV before runtime[/italic white]'
            '[bold blue] please set it before running the API[/bold blue]'
            '[italic yellow]\nUsing the Development Config as a fallback...[/italic yellow]'
        )


@lru_cache()
def running_config() -> AppConfig:
    '''LRU cache of the running AppConfig 
    Returns:
        AppConfig -- the running config
    '''
    instance = Settings.get_instance()
    if instance.config is None:
        Settings.load()
    return instance.config
