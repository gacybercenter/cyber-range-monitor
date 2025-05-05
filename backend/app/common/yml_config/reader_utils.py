import os
from typing import Any, Type, TypeVar
from pydantic import ValidationError
from pydantic_settings import BaseSettings
import yaml
import yaml

from app.common.schemas.errors import RunTimeValidationError
from pprint import pprint


def assert_path_exists(file_path: str) -> None:
    assert os.path.exists(file_path), (
        f"{file_path} does not exist ensure it exists and "
        "your current working directory is correct."
    )


def assert_paths_exist(file_paths: list[str]) -> None:
    for file_path in file_paths:
        assert_path_exists(file_path)


def open_yaml_file(file_path: str) -> dict:
    '''Opens a yaml file and returns the contents as a dictionary.

    Args:
        file_path (str): _the path to the yaml file_

    Returns:
        dict: _the contents of the yaml file_
    '''
    assert_path_exists(file_path)
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def section_not_found(section_name: str) -> str:
    return (
        f'The "{section_name}" section does not exist in the config file.\n'
        'Fix: Check for a typo in the section name of the .yaml file.'
    )


def load_yaml_section(
    settings_class: Type[BaseSettings],
    *,
    section_name: str,
    yaml_data: dict
) -> Any:
    '''Loads the settings for the plugin from the given options
    and nicely formats any validation errors that occur.

    Args:
        plugin_options (dict): _the options for the plugin_

    Raises:
        RunTimeValidationError: _if the schema is invalid_

    Returns:
        Self: setting instance
    '''
    if not section_name in yaml_data:
        raise RuntimeError(section_not_found(section_name))
    try:
        settings = settings_class(
            **yaml_data[section_name]
        )
    except ValidationError as exc:
        raise RunTimeValidationError(exc)
    return settings




