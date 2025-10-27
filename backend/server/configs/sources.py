import os
from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    SecretsSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


def parse_env_sequence(value: str, *, is_hashset: bool = False) -> set[str] | list[str]:
    seq = [item.strip() for item in value.split(',') if item.strip()]
    return set(seq) if is_hashset else seq


def get_app_env(override: str | None = None) -> str:
    return override or os.getenv('APP_ENV', 'dev')


class Config(BaseSettings):
    '''
    The base settings class for the application with
    quality of life settings set for environment variable
    handling.
    '''

    model_config = SettingsConfigDict(
        extra='ignore',
        validate_assignment=True,
    )


def get_dotenv_settings_source(
    settings_cls: type[BaseSettings],
    *,
    app_env: str | None = None,
) -> DotEnvSettingsSource:
    '''
    Gets a DotEnvSettingsSource for the given application
    environment

    Parameters
    ----------
    settings_cls : type[BaseSettings]
        The pydantic base settings class
    app_env : str | None, optional
        an app_env to override, by default None

    Returns
    -------
    DotEnvSettingsSource
        The DotEnvSettingsSource instance with
        the order from least to most specific
    '''
    app_env = app_env or get_app_env()
    load_order = ('example.env', '.env', f'.{app_env}.env')
    return DotEnvSettingsSource(
        settings_cls,
        case_sensitive=False,
        env_file=load_order,
        env_file_encoding='utf-8',
    )


def get_toml_config_source(
    settings_cls: type[BaseSettings],
    *,
    app_env: str | None = None,
) -> TomlConfigSettingsSource:
    '''
    Gets a TomlConfigSettingsSource for the given application environment
    from `APP_ENV` -> `app.{APP_ENV}.toml`, if that does not exist,
    falls back to `config.toml`.
    '''
    app_env = app_env or get_app_env()

    configs_dir = Path('configs')
    if not configs_dir.exists():
        raise FileNotFoundError(f'Configs directory not found at {configs_dir}')

    candidate = configs_dir / f'app.{app_env}.toml'
    if not candidate.exists():
        candidate = configs_dir / 'config.toml'

    return TomlConfigSettingsSource(settings_cls, toml_file=candidate)


def get_secret_settings_source(
    settings_cls: type[BaseSettings],
    *,
    app_env: str | None = None,
) -> SecretsSettingsSource:
    '''
    Gets a TomlConfigSettingsSource for secret settings
    from `APP_ENV` -> `secrets.{APP_ENV}.toml`, if that does not exist,
    falls back to `secrets.toml`.
    '''
    app_env = app_env or get_app_env()

    secrets_dir = 'secrets' if os.name == 'nt' else '/run/secrets'

    return SecretsSettingsSource(
        settings_cls,
        secrets_dir=secrets_dir,
    )
