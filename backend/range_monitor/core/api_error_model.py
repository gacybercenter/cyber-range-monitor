from typing import Annotated, Any

from pydantic import BaseModel, Field

ErrorType = Annotated[
    str,
    Field(description='A string representing the type of error that occurred'),
]
ErrorTitle = Annotated[
    str,
    Field(..., description='A short, human-readable summary of the error'),
]
ErrorStatus = Annotated[
    int,
    Field(..., description='The HTTP status code of the error response'),
]

ErrorDetail = Annotated[str, Field(description='A detailed description of the error')]
ErrorInstance = Annotated[str, Field(description='A Correlation ID of the request.')]

ErrorCode = Annotated[
    str,
    Field(description='An application-specific error code'),
]
ErrorExtras = Annotated[
    dict[str, Any], Field(description='A dictionary of additional error details')
]


class ErrorResponse(BaseModel):
    """
    The response schema for errors
    """

    error_type: ErrorType = 'about:blank'
    title: ErrorTitle
    status: ErrorStatus
    detail: ErrorDetail | None = None
    instance: ErrorInstance | None = None
    code: ErrorCode | None = None
    extras: ErrorExtras | None = None
