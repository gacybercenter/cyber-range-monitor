from pathlib import Path
from typing import Any, Type
from pydantic import ValidationError
from pydantic_settings import BaseSettings
import yaml

from app.common.schemas.errors import RunTimeValidationError
from app.utils import file_utils


def section_not_found(section_name: str) -> str:
    return (
        f'The "{section_name}" section does not exist in the config file.\n'
        "\n\tFix: Check for a typo in the section name of the .yaml file."
    )


def read_yaml(file_name: str) -> dict:
    """Opens a yaml file and returns the contents as a dictionary.

    Args:
        file_path (str): _the path to the yaml file_

    Returns:
        dict: _the contents of the yaml file_
    """

    yaml_path = file_utils.abs_root_path(file_name)

    file_utils.assert_path_exists(yaml_path)
    try:
        with yaml_path.open(mode="r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise RuntimeError(
            f"BuildFailed: Could not read the yaml file @{yaml_path}.\nDetails: {exc}"
        )


def section_to_settings(
    settings_class: Type[BaseSettings], *, section_name: str, yaml_data: dict
) -> Any:
    """Loads the settings for the plugin from the given options
    and nicely formats any validation errors that occur likely due
    to a typo, name mismatch or missing field.

    Args:
        plugin_options (dict): _the options for the plugin_

    Raises:
        RunTimeValidationError: _if the schema is invalid_

    Returns:
        the settings instance
    """
    if not section_name in yaml_data:
        raise RuntimeError(section_not_found(section_name))
    try:
        settings = settings_class(**yaml_data[section_name])
    except ValidationError as exc:
        raise RunTimeValidationError(exc)
    return settings
