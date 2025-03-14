
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigFieldDoc(BaseModel):
    """a class to represent the documentation of a field in a pydantic model
    used in the CLI for displaying the documentation
    """

    label: str
    name: str
    type_name: str
    default: str
    description: str
    required: str

    @classmethod
    def from_field_info(
        cls, name: str, config_label: str, from_cls: BaseSettings
    ) -> "ConfigFieldDoc":
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
            required="Yes" if field.is_required() else "No",
        )

    def to_row(self) -> list[str]:
        """a method to convert the instance to a list of strings
        used in the CLI for displaying the field as a row
        Returns:
            list[str]
        """
        return [
            self.label,
            self.name,
            self.type_name,
            self.default,
            self.description,
            self.required,
        ]


class SettingsMixin(BaseSettings):
    '''settings object with utility methods for CLI commands

    Returns:
        _type_ -- _description_
    '''
    model_config = SettingsConfigDict(extra="ignore")

    def get_docs(self, config_label: str) -> list[ConfigFieldDoc]:
        """a method to get the documentation of the fields in the model
        used in the CLI for displaying the documentation
        Returns:
            list[ConfigFieldDoc]
        """
        docs = []
        for name, _ in self.model_fields.items():
            doc = ConfigFieldDoc.from_field_info(name, config_label, self)
            docs.append(doc)
        return docs
    
        
        
    


