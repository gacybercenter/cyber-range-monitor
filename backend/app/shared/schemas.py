from datetime import datetime
from typing import Annotated

from fastapi import Path
from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field, 
    StringConstraints
)
from sqlalchemy import Select

# Generic Pydantic Models for the API


class StrictModel(BaseModel):
    """a placeholder (mostly) for now for constraints
    on models that should not allow extra fields
    """

    model_config = ConfigDict(extra="forbid")


FormUsername = Annotated[str, StringConstraints(
    min_length=3, 
    max_length=50, 
    pattern=r"^[a-zA-Z0-9_.-]+$"
)]

FormPassword = Annotated[str, StringConstraints(min_length=3, max_length=128)]

PathID = Annotated[int, Path(..., description="The id of model to act on.", gt=0)]


class AuthForm(StrictModel):
    """the constraints on inputs from the auth forms"""

    username: Annotated[FormUsername, Field(
        ..., 
        description="The username of the user (min length = 3, max length = 50)"
    )]
    password: Annotated[FormPassword, Field(
        ..., 
        description="The password of the user (min length = 3, max length = 128)"
    )]


def dt_serializer(dt: datetime) -> str:
    """the standardized format the API returns dates in"""
    return dt.strftime("%Y-%m-%d %H:%M")


class QueryFilters(StrictModel):
    """Standard query parameters for any route supporting Query Parameters"""

    skip: Annotated[
        int | None, Field(default=0, ge=0, description="The number of records to skip")
    ]
    limit: Annotated[
        int | None,
        Field(50, ge=1, le=1000, description="The number of records to return"),
    ]

    def apply_filter(self, stmnt: Select) -> Select:
        """Applies the skip and limit to the given SQLAlchemy Select statement"""
        if self.skip:
            stmnt = stmnt.offset(self.skip)

        if self.limit:
            stmnt = stmnt.limit(self.limit)

        return stmnt

    model_config = ConfigDict(extra="forbid")


class QueryResultData(StrictModel):
    """Information for the frontend on how to handle the results of a query
    and to build the next request for a given query.
    """

    total: int = Field(
        ..., 
        ge=0, 
        description="The total number of records from the returned query"
    )

    next_skip: int = Field(
        ...,
        ge=0,
        description="The number of records to skip for the next 'page' of the query",
    )

    num_page: int = Field(
        ..., ge=1, description="The number of pages of results from the query"
    )

    @classmethod
    def init(cls, total: int, skip: int, limit: int) -> "QueryResultData":
        return cls(
            total=total, next_skip=skip + limit, num_page=(total + limit - 1) // limit
        )


class ResponseMessage(BaseModel):
    """generic response returned to the client"""

    message: str = Field(..., description="A message to return to the client")
    success: bool = True


class QueryResponse(BaseModel):
    meta: QueryResultData = Field(
        ..., description="Metadata for the query results for the frontend to handle"
    )
    result: list[BaseModel] = Field(..., description="The results of the query")
