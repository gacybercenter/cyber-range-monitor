from typing import Annotated, Any

from pydantic import ConfigDict, Field

from range_monitor.core.schema import AliasGenerator, PydanticMixin

ErrorType = Annotated[
    str,
    Field(description='A string representing the type of error that occurred'),
]
ErrorStatus = Annotated[
    int,
    Field(..., description='The HTTP status code of the error response'),
]

ErrorDetail = Annotated[str, Field(
    description='A detailed description of the error')]
ErrorInstance = Annotated[str, Field(description='A Correlation ID of the request.')]

ErrorCode = Annotated[
    str,
    Field(description='An application-specific error code'),
]
ErrorExtras = Annotated[
    dict[str, Any], Field(description='A dictionary of additional error details')
]


class ErrorResponse(PydanticMixin):
    """
    The response schema for errors
    """
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=AliasGenerator.to_camel_case,
    )

    error_type: ErrorType = 'about:blank'
    status: ErrorStatus
    detail: ErrorDetail | None = None
    request_id: ErrorInstance | None = None
    code: ErrorCode | None = None
    extras: ErrorExtras | None = None
