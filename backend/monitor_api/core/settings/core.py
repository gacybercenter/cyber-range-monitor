import functools

from pydantic import ValidationError

from ..pydantic_utils import normalize_pydantic_exception
from .configs import AdapterSettings, EnvSettings


class InvalidSettingsError(Exception):

    def __init__(self, exc: ValidationError) -> None:
        details = [
            err.message()
            for err in normalize_pydantic_exception(exc)
        ]
        super().__init__(
            f'Build Failed, invalid configuration settings: {", ".join(details)}'
        )



@functools.lru_cache
def get_adapter_settings() -> AdapterSettings:
    """
    Gets the single cached instance of AdapterSettings.
    """
    try:
        return AdapterSettings()
    except ValidationError as exc:
        raise InvalidSettingsError(exc) from exc


@functools.lru_cache
def get_env_settings() -> EnvSettings:
    """
    gets the single cached instance of EnvSettings,
    using the env_file specified in the adapter config

    Returns
    -------
    APISettings
    """
    try:
        adapter_settings = get_adapter_settings()
        return EnvSettings(
            _env_file=adapter_settings.app.env_file  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        raise InvalidSettingsError(exc) from exc