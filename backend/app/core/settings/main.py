from ast import Dict
from functools import lru_cache
import os

import logging
from .secrets import SecretSettings, TempSecrets
from .app import app_settings
from .pyproject import PyProjectInfo


logger = logging.getLogger(__name__)


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
        logger.warning(
            f"Config file {app_settings.env_file} does not exist, "
            "using temp secrets, you may need to recreate the databse."
        )
        return TempSecrets()

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
