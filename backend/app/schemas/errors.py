import json
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from typing import Annotated, Optional

from fastapi import Request


def normalize_validation_error(err: ValidationError | RequestValidationError) -> list[dict]:
    '''normalizes the format of a validation error

    Arguments:
        err {ValidationError} -- the error raised

    Returns:
        list[dict]
    '''
    error_list = []
    for details in err.errors():
        error_list.append({
            'field': '.'.join(str(loc) for loc in details.get('loc', [])),
            'message': details.get('msg', ''),
            'type': details.get('type', '')
        })

    return error_list

class HTTPErrorDetails(BaseModel):
    '''The details of an error that occured during an HTTP request
    '''
    status: Annotated[int, Field(
        ...,
        description="The status code of the error"
    )]
    path: Annotated[str, Field(
        ...,
        description="The path that was accessed"
    )]
    method: Annotated[str, Field(
        ...,
        description="The HTTP method used"
    )]
    exc_details: Annotated[str, Field(
        ...,
        description="The details of the exception that was raised"
    )]
    headers: Annotated[Optional[str], Field(
        ...,
        description="The headers of the request that caused the error"
    )]

    def __repr__(self) -> str:
        return f"HTTPErrorDetails(status={self.status}, path={self.path}, method={self.method}, exc_details={self.exc_details}, headers={self.headers})"

    @classmethod
    def from_request(cls, request: Request, status: int, exc_details: str) -> "HTTPErrorDetails":
        return cls(
            status=status,
            path=request.url.path,
            method=request.method,
            exc_details=exc_details,
            headers=json.dumps(dict(request.headers))
        )


class APIErrorResponse(BaseModel):
    message: Annotated[str, Field(
        ...,
        description="A description of the error that occured"
    )]
    errors: Annotated[list[dict], Field(
        ...,
        description="A list of errors that occured during the request validation"
    )]
    error_label: Annotated[Optional[str], Field(
        ...,
        description="An optional label for the error"
    )]

    def __repr__(self) -> str:
        return f"APIErrorResponse(message={self.message})"

class APIInternalServerError(HTTPErrorDetails):
    '''The details of an internal server error
    '''
    stack_trace: Annotated[str, Field(
        ...,
        description="The stack trace of the error"
    )]
    
    @classmethod
    def from_request(cls, request: Request, status: int, exc_details: str, stack_trace: str) -> "APIInternalServerError":
        return cls(
            status=status,
            path=request.url.path,
            method=request.method,
            exc_details=exc_details,
            headers=json.dumps(dict(request.headers)),
            stack_trace=stack_trace
        )
    
    