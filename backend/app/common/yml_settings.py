import os
import yaml
from typing import Self

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError


from app.common.schemas.errors import RunTimeValidationError
from functools import lru_cache

SETTINGS_YAML_FILE = 'app.config.yaml'


@lru_cache(maxsize=1)
def get_build_config_yml() -> dict:
    if not os.path.exists(SETTINGS_YAML_FILE):
        raise FileNotFoundError(
            f"{SETTINGS_YAML_FILE} does not exist ensure it exists and your current working directory is correct."
        )

    with open(SETTINGS_YAML_FILE, 'r') as f:
        plugin_config = yaml.safe_load(f)

    return plugin_config


def get_yml_file_section(section: str) -> dict:
    data = get_build_config_yml().get(section)
    if not data:
        raise RuntimeError(
            f'The "{section}" section does not exist in the config file.'
            ' Check for a typo in the section name'
        )
    return data


class YMLBuildSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra='ignore'
    )

    @classmethod
    def load(cls, plugin_options: dict) -> 'Self':
        '''Loads the settings for the plugin from the given options
        and nicely formats any validation errors that occur.

        Args:
            plugin_options (dict): _the options for the plugin_

        Raises:
            RunTimeValidationError: _if the schema is invalid_

        Returns:
            Self: setting instance
        '''
        try:
            return cls(
                **plugin_options
            )
        except ValidationError as e:
            raise RunTimeValidationError(e)
