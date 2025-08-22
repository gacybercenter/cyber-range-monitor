


import functools

from .adapter_configs import AdapterConfigYaml
from .env_configs import APISettings


@functools.lru_cache
def get_adapter_settings() -> AdapterConfigYaml:
    """
    Returns the adapter settings loaded from a YAML file.

    Returns
    -------
    AdapterConfigYaml
        The adapter settings instance.
    """
    return AdapterConfigYaml()

@functools.lru_cache
def get_api_settings() -> APISettings:
    """
    Returns the API settings loaded from environment variables or a `.env` file.

    Returns
    -------
    APISettings
        The API settings instance.
    """
    env_file = get_adapter_settings().env_file

    return APISettings(
        _env_file=env_file,  # type: ignore[return-value]
    )
