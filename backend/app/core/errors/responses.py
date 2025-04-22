from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from fastapi.exceptions import RequestValidationError


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



class APIErrorResponse(HTTPExcDetails):
    '''The response returned when an error occurs during an API request'''

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    def __repr__(self) -> str:
        return f"APIErrorResponse(message={self.message})"


