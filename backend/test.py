from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class ProjectConfig(BaseSettings):
    name: str 
    version: str
    description: str

    @classmethod
    def settings_customise_sources(
        cls, 
        settings_cls: BaseSettings, 
        init_settings: PydanticBaseSettingsSource, 
        env_settings: PydanticBaseSettingsSource, 
        dotenv_settings: PydanticBaseSettingsSource, 
        file_secret_settings: PydanticBaseSettingsSource
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            PyprojectTomlConfigSettingsSource(cls),
        )
    
    model_config = SettingsConfigDict(
        toml_file='pyproject.toml',
        pyproject_toml_table_header=('project',),
        extra='ignore'
    )

def main() -> None:
    config = ProjectConfig()
    print(config.model_dump())

if __name__ == '__main__':
    main()