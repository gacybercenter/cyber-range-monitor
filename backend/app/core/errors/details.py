import json
from typing import Annotated, Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class PydanticError(BaseModel):
    field: Annotated[str, Field(
        ..., description="The field that caused the error"
    )]
    message: Annotated[str, Field(..., description="The error message")]
    type: Annotated[str, Field(..., description="The type of error")]

class HTTPExcDetails(BaseModel):
    '''Defines the "details" returned by the API when an error occurs'''
    message: Annotated[
        str, Field(..., description="A description of the error that occured")
    ]
    success: bool = False
    error_label: Annotated[Optional[str], Field(
        None,
        description="An optional label for the error for errors that share status codes but have different meanings"
    )]

class HTTPValidationErrorDetails(HTTPExcDetails):
    message: str = "Invalid data."
    errors: list[PydanticError]

def normalize_validation_error(
    err: ValidationError | RequestValidationError,
) -> list[PydanticError]:
    """normalizes the format of a validation error

    Arguments:
        err {ValidationError} -- the error raised

    Returns:
        list[dict] -- the errors in a normalized format
    """
    error_list = []
    for details in err.errors():
        error_data = PydanticError(
            field=".".join(str(loc) for loc in details.get("loc", [])),
            message=details.get("msg", "Invalid data."),
            type=details.get("type", "Unknown"),
        )
        error_list.append(error_data)

    return error_list

class APIErrorResponse(HTTPExcDetails):
    '''The response returned when an error occurs during an API request'''

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    def __repr__(self) -> str:
        return f"APIErrorResponse(message={self.message})"


