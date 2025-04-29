

from ast import Dict
from functools import lru_cache
import os

from .secrets import SecretSettings, TempSecrets
from .app import app_settings
from .pyproject import PyProjectInfo


@lru_cache(maxsize=1)
def get_secret_settings() -> SecretSettings:
    """returns the secrets from the config.yml file
    the LRU cache allows for the value to be computed once and reused
    in subsequent calls
    Returns:
        SecretSettings -- the secrets from the config.yml file
    """
    if app_settings.testing:
        return TempSecrets()

    if not os.path.exists(app_settings.env_file):
        raise FileNotFoundError(
            "The secrets file does not exist, "
            "run the following command 'uv run python -m scripts.create_env' to create them."
        )

    return SecretSettings(
        _env_file=app_settings.env_file,  # type: ignore
    )


def get_pyproject() -> PyProjectInfo:
    """returns the pyproject.toml info, not cached because it's only
    used once when the app is created
    Returns:
        PyProjectInfo -- the pyproject.toml info
    """
    return PyProjectInfo()  # type: ignore
