from datetime import datetime

from typing import Any, Self, TypeVar
from pydantic import BaseModel, ConfigDict

from datetime import datetime

from . import serializer


class CustomBaseModel(BaseModel):
    """The base model for all app models allowing for standard serialization
    and deserialization of ambiguous types such as datetime, globally allow
    camel case in the body of requests and responses and also allows for
    the use of enums as values in the models
    """

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        from_attributes=True,
        alias_generator=serializer.to_camel,
        json_encoders={
            datetime: serializer.datetime_string
        }
    )

    @classmethod
    def convert(cls, obj_in: Any) -> Self:
        """converts the input object to the model class
        Returns:
            Self -- the type of the inheriting class
        """
        return cls.model_validate(obj=obj_in, from_attributes=True)

    def serialize(self) -> dict:
        """the standard arguments for .model_dump()
        to generalize behaviors across all models.
        Returns:
            dict - the dictionary representation of 
            the model
        """
        return self.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

    def serialize_exclude(self, exclude: set[str]) -> dict:
        """the standard arguments for .model_dump()
        to generalize behaviors across all models w/ exclusions.
        Returns:
            dict - the dictionary representation of 
            the model
        """
        return self.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude=exclude
        )


SchemaT = TypeVar("SchemaT", bound=CustomBaseModel)
