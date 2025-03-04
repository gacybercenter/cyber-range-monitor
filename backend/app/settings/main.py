from functools import lru_cache

from pydantic_settings import BaseSettings

from .errors import InvalidConfigYAML, SecretsNotFound
from .secrets import APISecrets
from .static import PyProjectInfo, SettingsYml, static_config_map


@lru_cache
def get_config_yml() -> SettingsYml:
    """returns the settings from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        SettingsYml -- the static settings from the config.yml file
    """
    try:
        return SettingsYml()  # type: ignore
    except Exception as e:
        raise InvalidConfigYAML(e) from e


@lru_cache
def get_secrets() -> APISecrets:
    """returns the secrets from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        APISecrets -- the secrets from the config.yml file
    """
    app_config = get_config_yml().app
    secret_path = app_config.secrets_file_path()
    if app_config.environment == "local" and not secret_path.exists():
        raise SecretsNotFound(str(secret_path))
    try:
        return APISecrets(_env_file=str(secret_path))  # type: ignore
    except Exception as e:
        raise SecretsNotFound(str(secret_path)) from e


def config_model_map() -> dict[str, type[BaseSettings]]:
    """returns the mapping of a string prefix to a base setting model type
    for use in the CLI without circular imports
    Returns:
        dict[str, type] -- the mapping of config types to their models
    """
    return static_config_map
    
    
def get_pyproject() -> PyProjectInfo:
    """returns the pyproject.toml info, not cached because it's only
    used once when the app is created
    Returns:
        PyProjectInfo -- the pyproject.toml info
    """
    return PyProjectInfo()  # type: ignore
