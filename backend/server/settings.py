import contextlib
import functools

from pydantic import ValidationError as PydanticValidationError

from server.configs.secrets import SecretSettings
from server.configs.toml import AppTomlSettings
from server.exceptions import RuntimeValidationError


@contextlib.contextmanager
def _format_validation_errors():  # noqa: ANN202
    try:
        yield
    except PydanticValidationError as orig:
        raise RuntimeValidationError(orig) from orig


@functools.lru_cache
def get_app_settings() -> AppTomlSettings:
    with _format_validation_errors():
        return AppTomlSettings()


@functools.lru_cache
def get_secret_settings() -> SecretSettings:
    with _format_validation_errors():
        return SecretSettings()  # type: ignore
