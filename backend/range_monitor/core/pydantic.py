import hashlib
from typing import Any, Literal, Self

import orjson
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_core import ErrorDetails


class AliasGenerators:
    '''
    Alias generators for pydantic models
    '''
    @staticmethod
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

    @staticmethod
    def kebab_case(string: str) -> str:
        return ''.join('-' + c.lower() if c.isupper() else c for c in string).lstrip(
            '-'
        )


class PydanticError(BaseModel):
    '''
    Normalized standard format for Pydantic validation errors
    '''
    field: str
    detail: str
    type: str

    def message(self) -> str:
        return f'Error on field "{self.field}": {self.detail} (type={self.type})'

    @classmethod
    def parse_details(cls, details: ErrorDetails | Any) -> 'PydanticError':
        '''
        Parses a single `ErrorDetails` from a validation error PydanticError
        into a human readable format
        Parameters
        ----------
        details : ErrorDetails | Any

        Returns
        -------
        PydanticError
        '''
        loc = details.get('loc', ())
        if not loc:
            field = ''
        else:
            field = '.'.join(str(x) for x in loc)

        return cls(
            field=field,
            detail=details.get('msg', 'Unknown error'),
            type=details.get('type', 'unknown_error'),
        )



class SchemaUtils:
    '''
    Utility class for common schema operations

    Returns
    -------
    '''
    @staticmethod
    def as_headers(schema: 'PydanticMixin', *, prefix: str | None = None) -> dict[str, str]:
        """
        Utility function to convert a pydantic schema to a dictionary
        of HTTP headers. The keys are converted to kebab-case and
        prefixed if a prefix is provided.

        Parameters
        ----------
        schema : PydanticMixin
            The pydantic schema to convert to headers.
        prefix : str | None, optional
            The prefix to add to each header key, by default None.

        Returns
        -------
        dict[str, str]
            A dictionary of HTTP headers.
        """
        headers = {}
        base = schema.dump()
        for k, v in base.items():
            if v is None:
                continue
            key = AliasGenerators.kebab_case(k)
            if prefix:
                key = f'{prefix}-{key}'
            headers[key] = str(v)
        return headers

    @staticmethod
    def get_only_set_fields(schema: 'PydanticMixin') -> dict[str, Any]:
        """
        Utility function to get only the fields that were explicitly set
        in a pydantic schema. This is useful for PATCH operations where
        only the fields that were set by the user should be updated.

        Parameters
        ----------
        schema : PydanticMixin
            The pydantic schema to get the set fields from.

        Returns
        -------
        dict[str, Any]
            A dictionary of the fields that were explicitly set in the schema.
        """
        return {k: getattr(schema, k) for k in schema.model_fields_set}

    @staticmethod
    def get_pydantic_errors(exception: ValidationError | RequestValidationError) -> list[PydanticError]:
        '''
        Parses a pydantic ValidationError or RequestValidationError
        into a list of human readable PydanticError objects.

        Parameters
        ----------
        exception : ValidationError | RequestValidationError

        Returns
        -------
        list[PydanticError]
        '''
        return [PydanticError.parse_details(err) for err in exception.errors()]


class PydanticMixin(BaseModel):
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


    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.json()}>'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.stable_hash() == value.stable_hash()

class AliasGenerator:
    @staticmethod
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

    @staticmethod
    def kebab_case(string: str) -> str:
        return string.replace('_', '-').lower()
