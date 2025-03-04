from typing import Self
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class ConfigFieldDoc(BaseSettings):
    '''a class to represent the documentation of a field in a pydantic model
    used in the CLI for displaying the documentation
    '''
    label: str
    name: str
    type_name: str
    default: str
    description: str
    required: str

    @classmethod
    def from_field_info(
        cls,
        name: str,
        config_label: str,
        from_cls: BaseSettings
    ) -> 'ConfigFieldDoc':
        """a method to create a ConfigFieldDoc instance from a field name
        used in the CLI for displaying the documentation

        Arguments:
            name {str} -- the name of the field

        Returns:
            None
        """
        field = from_cls.model_fields[name]
        type_name = field.annotation.__name__ if field.annotation else "Unknown"
        return cls(
            label=config_label,
            name=name,
            type_name=type_name,
            default=str(field.default) if field.default else "None",
            description=field.description if field.description else "No description",
            required="Yes" if field.is_required() else "No"
        )

    def to_row(self) -> list[str]:
        '''a method to convert the instance to a list of strings
        used in the CLI for displaying the field as a row
        Returns:
            list[str]
        '''
        return [
            self.label,
            self.name,
            self.type_name,
            self.default,
            self.description,
            self.required
        ]


class SettingsMixin(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore"
    )

    def get_docs(self, config_label: str) -> list[ConfigFieldDoc]:
        '''a method to get the documentation of the fields in the model
        used in the CLI for displaying the documentation
        Returns:
            list[ConfigFieldDoc]
        '''
        docs = []
        for name, field in self.model_fields.items():
            doc = ConfigFieldDoc.from_field_info(
                name,
                config_label,
                self
            )
            docs.append(doc)
        return docs


class YamlBaseSettings(SettingsMixin):
    """the setup for reading the yml file in pydantic_settings"""

    model_config = SettingsConfigDict(
        yaml_file="config.yml",
        yaml_file_encoding="utf-8",
        env_nested_delimiter="__"
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
        """ensures the yaml file is loaded first, internal to pydantic_settings

        Arguments:
            settings_cls {type[BaseSettings]}
            init_settings {PydanticBaseSettingsSource}
            env_settings {PydanticBaseSettingsSource}
            dotenv_settings {PydanticBaseSettingsSource}
            file_secret_settings {PydanticBaseSettingsSource}

        Returns:
            tuple[PydanticBaseSettingsSource, ...] -- _description_
        """
        yaml_settings = YamlConfigSettingsSource(settings_cls=settings_cls)
        return (
            yaml_settings,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


class SecretSettings(BaseSettings):
    '''the setup for reading the secret file in pydantic_settings'''
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @classmethod
    def from_env_file(cls, env_file_name: str) -> Self:
        return cls(_env_file=env_file_name) # type: ignore
