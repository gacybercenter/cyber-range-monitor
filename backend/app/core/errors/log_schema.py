from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import Request




class HTTPErrorDetails(BaseModel):
    """The details of an error that occured during an HTTP request, internal use only"""

    status: Annotated[int, Field(
        ..., description="The status code of the error"
    )]
    path: Annotated[str, Field(..., description="The path that was accessed")]
    method: Annotated[str, Field(..., description="The HTTP method used")]
    exc_details: Annotated[
        str, Field(..., description="The details of the exception that was raised")
    ]

    def __str__(self) -> str:
        return f"HTTP Error {self.status} | @{self.path} [{self.method}] - {self.exc_details}"

    @classmethod
    def from_request(
        cls, request: Request, status: int, exc_details: str
    ) -> "HTTPErrorDetails":
        return cls(
            status=status,
            path=request.url.path,
            method=request.method,
            exc_details=exc_details
        )
