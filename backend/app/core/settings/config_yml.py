from .schemas import (
    AppConfig,
    DocumentationConfig,
    DatabaseConfig,
    RedisConfig,
    AuthConfig,
    CORSPolicyConfig
)

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource
)


class YMLAppSettings(BaseSettings):
    """the setup for reading the yml file in pydantic_settings"""
    app: AppConfig
    database: DatabaseConfig
    auth: AuthConfig
    redis: RedisConfig
    cors: CORSPolicyConfig
    documentation: DocumentationConfig

    model_config = SettingsConfigDict(
        yaml_file="config.yml",
        yaml_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra='ignore'
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """ensures the yaml file is loaded first, internal to pydantic_settings"""
        yaml_settings = YamlConfigSettingsSource(settings_cls=settings_cls)
        return (
            yaml_settings,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings
        )
