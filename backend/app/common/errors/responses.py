from typing import Annotated, List, Literal, Self

from fastapi.exceptions import RequestValidationError
from pydantic import ConfigDict, Field

from app.common.schemas.errors import (
    PydanticErrorMeta, 
    from_validation_error,
    CustomBaseModel
)


class HTTPErrorSchema(CustomBaseModel):
    '''Defines the "details" returned by the API when an error occurs'''
    message: Annotated[str, Field(
        ...,
        description="A description of the error that occured"
    )]
    success: Annotated[Literal[False], Field(
        False,
        description="Explicitly indicates failure"
    )] = False
    status_text: Annotated[str, Field(
        ...,
        description="The status text of the error"
    )]


class HTTPValidationError(HTTPErrorSchema):
    message: str = "Invalid request data"
    errors: Annotated[List[PydanticErrorMeta], Field(
        ...,
        description="A list of errors that occurred during validation"
    )]

    @classmethod
    def from_exc(cls, exc: RequestValidationError) -> Self:
        return cls(
            errors=from_validation_error(exc),
            status_text='UNPROCESSABLE ENTITY',
            success=False
        )


class HTTPErrorResponse(HTTPErrorSchema):
    '''The response returned when an error occurs during an API request'''

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    def __repr__(self) -> str:
        return f"APIErrorResponse(message={self.message})"
