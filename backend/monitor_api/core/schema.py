import hashlib

from typing import Any, Literal, Self

import orjson

from pydantic import BaseModel, ConfigDict


def to_camel_case(string: str) -> str:
    """
    Pydantic alias generator to convert snake_case to camelCase
    when `model_dump()` is called which automatically makes snake
    case to camel case conversions for keys in dicts.
    """
    words = string.split('_')
    new_name = []
    for i, word in enumerate(words):
        if i:
            new_name.append(word.capitalize())
        else:
            new_name.append(word.lower())

    return ''.join(new_name).replace('Id', 'ID')


class SchemaMixin(BaseModel):
    """
    The base pydantic schema for use in all pydantic models
    with common utility methods to standardize behavior.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        validate_default=True,
        from_attributes=True,
        str_strip_whitespace=True,
        ser_json_timedelta='iso8601',
    )

    @classmethod
    def convert(cls, obj_in: Any) -> Self:
        """
        Calls `model_validate` to convert an object into the
        pydantic model with `from_attributes=True` to allow
        conversion from ORM models.

        Parameters
        ----------
        obj_in : Any

        Returns
        -------
        Self
        """
        return cls.model_validate(obj=obj_in, from_attributes=True)

    def dump(
        self,
        *,
        exclude_none: bool = True,
        exclude_unset: bool = False,
        mode: Literal['json', 'python'] = 'python',
        by_alias: bool = True,
    ) -> dict:
        """
        utility `.model_dump()` method to generalize behaviors across
        all models.
        Sets `exclude_unset=True` and `exclude_none=True`

        Returns
        -------
        dict
        """
        return self.model_dump(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            mode=mode,
            by_alias=by_alias,
        )

    def json(
        self,
        *,
        by_alias: bool = True,
        exclude_none: bool = True,
    ) -> str:
        """
        utility `.model_dump_json()` method to generalize behaviors across
        all models.
        Sets `exclude_none=True` and `by_alias=True` by default.

        Returns
        -------
        str
        """
        schema = self.dump(
            by_alias=by_alias,
            exclude_none=exclude_none,
        )
        return orjson.dumps(schema, option=orjson.OPT_NON_STR_KEYS).decode()

    def stable_hash(self) -> str:
        """
        Stable schema hash (good for cache keys / idempotency keys)
        using sha256 over the jsonable dict representation. The keys
        are sorted to ensure stability.
        """
        payload = self.dump()
        b = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)

        return hashlib.sha256(b).hexdigest()


class CamelCaseSchema(SchemaMixin):
    """
    A pydantic schema that uses camelCase keys when `.model_dump(by_alias=True)`
    is called. This is useful for APIs that follow camelCase conventions.
    """

    model_config = ConfigDict(alias_generator=to_camel_case)
