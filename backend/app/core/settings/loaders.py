

import contextlib
import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from pydantic_settings import BaseSettings

from app.core import path_utils

from ..exceptions import RuntimeValidationError
from . import toml_utils


@contextlib.contextmanager
def validation_error_handle():
    try:
        yield
    except ValidationError as exc:
        raise RuntimeValidationError(exc) from exc


@dataclass
class TomlConfigLoader:
    toml_file: str

    @property
    def config_path(self) -> Path:
        app_root = path_utils.get_app_root()
        return app_root / self.toml_file

    @functools.cached_property
    def config_dict(self) -> dict:
        return toml_utils.read_toml(self.config_path)

    def load(
        self,
        settings_class: type[BaseSettings],
        *,
        section_name: str,
    ) -> Any:
        """
        Load settings from the TOML file.

        Parameters
        ----------
        settings_class : type[BaseSettings]
            The settings class to load.
        section_name : str
            The section name in the TOML file.

        Returns
        -------
        BaseSettings
            An instance of the settings class with loaded values.
        """
        toml_data = self.config_dict
        if not toml_data:
            raise RuntimeError('Nothing was loaded from the TOML file.')

        try:
            section = toml_utils.get_toml_section(section_name, toml_data)
        except KeyError as exc:
            raise RuntimeError(
                f"Section '{section_name}' not found in TOML data."
            ) from exc

        with validation_error_handle():
            settings = settings_class.model_validate(section)

        return settings

@dataclass(slots=True)
class SecretsLoader:
    env_file: str
    is_testing: bool = False

    def get_env_path(self) -> Path:
        """
        Returns the path to the environment file.
        """
        return path_utils.get_app_root().joinpath(self.env_file)

    def load(
        self,
        settings_class: type[BaseSettings],
        *,
        env_file: str | None = None,
        testing_fallback_cls: type[BaseSettings] | None = None,
    ) -> Any:
        '''
        Load settings from the environment file.

        Parameters
        ----------
        settings_class : type[BaseSettings]
        env_file : str | None, optional
            _An override env file to use_, by default None
        testing_fallback_cls : type[BaseSettings] | None, optional
            _A tetsing fallback class to use_, by default None

        Returns
        -------
        Any
        '''
        env_file = env_file or self.env_file
        if testing_fallback_cls and self.is_testing:
            return testing_fallback_cls()

        return settings_class(
            _env_file=env_file,
        )
