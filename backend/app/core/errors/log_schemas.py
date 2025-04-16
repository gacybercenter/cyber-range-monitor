

from typing import Annotated

from fastapi import Request
from pydantic import BaseModel, Field

import json

class HTTPErrorDetails(BaseModel):
    """The details of an error that occured during an HTTP request, internal use only"""

    status: Annotated[int,Field(
        ..., description="The status code of the error"
    )]
    path: Annotated[str, Field(..., description="The path that was accessed")]
    method: Annotated[str, Field(..., description="The HTTP method used")]
    exc_details: Annotated[
        str, Field(..., description="The details of the exception that was raised")
    ]
    headers: Annotated[
        str | None,
        Field(..., description="The headers of the request that caused the error"),
    ]

    def __repr__(self) -> str:
        return f"HTTPErrorDetails(status={self.status}, path={self.path}, method={self.method}, exc_details={self.exc_details}, headers={self.headers})"

    @classmethod
    def from_request(
        cls, request: Request, status: int, exc_details: str
    ) -> "HTTPErrorDetails":
        return cls(
            status=status,
            path=request.url.path,
            method=request.method,
            exc_details=exc_details,
            headers=json.dumps(dict(request.headers)),
        )


class InternalServerErrorData(HTTPErrorDetails):
    """The details of an internal server error"""

    stack_trace: Annotated[str,
                           Field(..., description="The stack trace of the error")]

    @classmethod
    def from_request(
        cls, request: Request, status: int, exc_details: str, stack_trace: str
    ) -> "InternalServerErrorData":
        return cls(
            status=status,
            path=request.url.path,
            method=request.method,
            exc_details=exc_details,
            headers=json.dumps(dict(request.headers)),
            stack_trace=stack_trace
        )
