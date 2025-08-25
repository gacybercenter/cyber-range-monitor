from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

if TYPE_CHECKING:
    from typing import TypeVar

    from pydantic_core import ErrorDetails

    from .schema import SchemaMixin

    S = TypeVar('S', bound=SchemaMixin)


def copy_update_schema(
    schema: 'S',
    **updates: Any,
) -> 'S':
    """
    Utility function to copy and update a pydantic schema.
    This is useful for creating new instances of a schema
    with some fields updated.

    Parameters
    ----------
    schema : S
        The pydantic schema to copy and update.
    **updates : Any
        The fields to update in the new schema.

    Returns
    -------
    S
        A new instance of the schema with the updates applied.
    """
    return schema.model_copy(update=updates, deep=True)


def _to_kebab_case(s: str) -> str:
    return ''.join('-' + c.lower() if c.isupper() else c for c in s).lstrip('-')


def only_set_fields(schema: 'SchemaMixin') -> dict[str, Any]:
    """
    Utility function to get only the fields that were explicitly set
    in a pydantic schema. This is useful for PATCH operations where
    only the fields that were set by the user should be updated.

    Parameters
    ----------
    schema : S
        The pydantic schema to get the set fields from.

    Returns
    -------
    dict[str, Any]
        A dictionary of the fields that were explicitly set in the schema.
    """
    return {k: getattr(schema, k) for k in schema.model_fields_set}


def as_headers(schema: 'SchemaMixin', *, prefix: str | None = None) -> dict[str, str]:
    """
    Utility function to convert a pydantic schema to a dictionary
    of HTTP headers. The keys are converted to kebab-case and
    prefixed if a prefix is provided.

    Parameters
    ----------
    schema : SchemaMixin
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
        key = _to_kebab_case(k)
        if prefix:
            key = f'{prefix}-{key}'
        headers[key] = str(v)
    return headers


def _join_field_loc(loc: tuple[str | int, ...]) -> str:
    if not loc:
        return ''
    return '.'.join(str(x) for x in loc)

@dataclass(slots=True)
class PydanticError:
    field: str
    detail: str
    type: str

    def message(self) -> str:
        return f'Error for Field "{self.field}": {self.detail} ({self.type})'

    @classmethod
    def parse(cls, details: ErrorDetails | Any) -> 'PydanticError':
        return cls(
            field=_join_field_loc(details.get('loc', ())),
            detail=details.get('msg', 'Unknown error'),
            type=details.get('type', 'unknown_error'),
        )

def normalize_pydantic_exception(
    details: ValidationError | RequestValidationError
) -> list[PydanticError]:
    '''
    Normalizes pydantic validation errors into a list of PydanticError

    Parameters
    ----------
    details : ValidationError | RequestValidationError

    Returns
    -------
    list[PydanticError]
    '''
    return [
        PydanticError.parse(err) for err in details.errors()
    ]



