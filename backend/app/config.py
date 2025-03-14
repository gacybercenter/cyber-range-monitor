from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

from app.core.settings.pyproject_info import PyProjectInfo
from app.core.settings.secrets import APISecrets, TempSecrets
from app.core.settings.config_yml import YMLAppSettings


@lru_cache
def get_config_yml() -> YMLAppSettings:
    """returns the settings from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        SettingsYml -- the static settings from the config.yml file
    """
    return YMLAppSettings()  # type: ignore


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
    if app_config.testing or app_config.env_file == 'temp':
        return TempSecrets()
    if app_config.environment == "local" and not secret_path.exists():
        raise FileNotFoundError(
            "The secrets file does not exist, "
            "run the following command 'uv run python -m scripts.create_env' to them."
        )
    return APISecrets(
        _env_file=str(secret_path)  # type: ignore
    )


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
    from app.core.settings.schemas import settings_map
    return settings_map
