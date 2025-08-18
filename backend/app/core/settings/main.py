from typing import Final

from .app import AppConfig
from .loaders import SecretsLoader, TomlConfigLoader

TOML_CONFIG_FILE: Final[str] = 'config.toml'
TomlLoader: Final[TomlConfigLoader] = TomlConfigLoader(
    toml_file=TOML_CONFIG_FILE,
)

_app_config: Final[AppConfig] = TomlLoader.load(
    AppConfig,
    section_name='app',
)
SecretLoader: Final[SecretsLoader] = SecretsLoader(
    env_file=_app_config.env_file,
    is_testing=_app_config.testing,
)


def get_app_settings() -> AppConfig:
    """
    Get the application settings.

    Returns
    -------
    AppConfig
    """
    return _app_config
