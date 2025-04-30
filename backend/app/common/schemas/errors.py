from typing import Annotated, Any, List, Self

from fastapi.exceptions import RequestValidationError
from pydantic import Field, ValidationError
from pydantic_core import ErrorDetails

from .base import CustomBaseModel


class PydanticErrorMeta(CustomBaseModel):
    field: Annotated[str, Field(
        ..., description="The field that caused the error"
    )]
    message: Annotated[str, Field(..., description="The error message")]
    type: Annotated[str, Field(..., description="The type of error")]

    @classmethod
    def create(cls, details: ErrorDetails | Any) -> Self:
        """creates a new PydanticErrorMeta object from the error details

        Arguments:
            details {ErrorDetails} -- the error details

        Returns:
            PydanticErrorMeta -- the new PydanticErrorMeta object
        """
        field_name = ".".join(str(loc) for loc in details.get("loc", []))
        message = details.get("msg", "Invalid data.")
        error_type = details.get("type", "Unknown")
        return cls(
            field=field_name,
            message=message,
            type=error_type
        )

    def __str__(self) -> str:
        return (
            f'\nValidationError\n\tField: {self.field}\n\t'
            f'Error Type: {self.type}\n\tError Message: {self.message}\n'
        )

    def __repr__(self) -> str:
        return str(self)


def from_validation_error(
    err: ValidationError | RequestValidationError
) -> List[PydanticErrorMeta]:
    """normalizes the format of a validation error

    Arguments:
        err {ValidationError} -- the error raised

    Returns:
        list[dict] -- the errors in a normalized format
    """
    error_list = []
    for details in err.errors():
        error_data = PydanticErrorMeta.create(
            details=details
        )
        error_list.append(error_data)

    return error_list


class RunTimeValidationError(Exception):
    """A custom validation error that is raised when a runtime validation error occurs"""

    def __init__(self, orig_exc: ValidationError) -> None:
        errors = from_validation_error(orig_exc)
        message = [str(error) for error in errors]
        super().__init__(f"\nRunTimeValidationError: \n{message}")
