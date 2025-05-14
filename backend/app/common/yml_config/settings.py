from typing import Dict, Self

from pydantic_settings import BaseSettings, SettingsConfigDict

import functools

from . import yaml_utils

SETTINGS_FILE_NAME = "app.config.yaml"


@functools.lru_cache(maxsize=1)
def get_app_config_file() -> Dict:
    """Reads / Caches the contents of the build config file.

    Returns:
        Dict: _the cached contents of the_
    """
    return yaml_utils.read_yaml(file_name=SETTINGS_FILE_NAME)


class YAMLSettings(BaseSettings):
    """Represents settings loaded from a YAML file."""

    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    @classmethod
    def create(cls, *, section_name: str) -> "Self":
        """Loads the settings for the plugin from the given options
        and nicely formats any validation errors that occur.

        Args:
            plugin_options (dict): _the options for the plugin_

        Raises:
            RunTimeValidationError: _if the schema is invalid_

        Returns:
            Self: setting instance
        """
        file_cache = get_app_config_file()

        return yaml_utils.section_to_settings(
            settings_class=cls, section_name=section_name, yaml_data=file_cache
        )
