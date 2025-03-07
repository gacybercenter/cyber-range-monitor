from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

from app.core.settings.pyproject_info import PyProjectInfo
from app.core.settings.secrets import APISecrets
from app.core.settings.schemas import (
    AppConfig,
    AppSettings,
    DatabaseConfig,
    DocumentationConfig,
    RedisConfig,
    APIKeyConfig
)

static_config_map = {
    "documentation": DocumentationConfig,
    "database": DatabaseConfig,
    "redis": RedisConfig,
    "api_key": APIKeyConfig,
    "app": AppConfig
}


@lru_cache
def get_config_yml() -> AppSettings:
    """returns the settings from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        SettingsYml -- the static settings from the config.yml file
    """
    return AppSettings()  # type: ignore


@lru_cache
def get_secrets() -> APISecrets:
    """returns the secrets from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        APISecrets -- the secrets from the config.yml file
    """
    app_config = get_config_yml().app
    secret_path = Path(app_config.env_file)
    if app_config.environment == "local" and not secret_path.exists():
        raise FileNotFoundError(f"No secrets file found at {secret_path}")

    return APISecrets(_env_file=str(secret_path))  # type: ignore


def get_api_key_config() -> APIKeyConfig:
    """returns the api key config from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        APIKeyConfig -- the api key config from the config.yml file
    """
    return get_config_yml().api_key


def get_app_config() -> AppConfig:
    """returns the app config from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        AppConfig -- the app config from the config.yml file
    """
    return get_config_yml().app


def get_database_config() -> DatabaseConfig:
    """returns the database config from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        DatabaseConfig -- the database config from the config.yml file
    """
    return get_config_yml().database


def get_redis_config() -> RedisConfig:
    """returns the redis config from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        RedisConfig -- the redis config from the config.yml file
    """
    return get_config_yml().redis


def get_documentation_config() -> DocumentationConfig:
    """returns the documentation config from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        DocumentationConfig -- the documentation config from the config.yml file
    """
    return get_config_yml().documentation


def get_pyproject() -> PyProjectInfo:
    """returns the pyproject.toml info, not cached because it's only
    used once when the app is created
    Returns:
        PyProjectInfo -- the pyproject.toml info
    """
    return PyProjectInfo()  # type: ignore


def config_model_map() -> dict[str, type[BaseSettings]]:
    """returns the mapping of a string prefix to a base setting model type
    for use in the CLI without circular imports
    Returns:
        dict[str, type] -- the mapping of config types to their models
    """
    return static_config_map  # type: ignore
