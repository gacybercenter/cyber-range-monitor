import math
from datetime import datetime
from typing import Generic, Literal, Self, TypeVar

from pydantic import ConfigDict, Field
from fastapi import Query
from app.core.pydantic import CustomBaseModel, PositiveNumber


class RequestSchema(CustomBaseModel):
    """The base request schema for all API requests"""

    model_config = ConfigDict(extra="forbid", strict=True)


class ResponseSchema(CustomBaseModel):
    """the base response schema for all API responses"""


class PageInfo(ResponseSchema):
    page: PositiveNumber = Field(1, description="The current page number (1 indexed)")

    page_size: PositiveNumber = Field(10, description="The number of items per page")
    total: int = Field(0, description="The total number of items available", ge=0)
    total_pages: int = Field(0, description="The total number of pages available", ge=0)
    has_next: bool = Field(False, description="Whether there is a next page available")
    has_previous: bool = Field(
        False, description="Whether there is a previous page available"
    )
    previous_page: int | None = Field(
        None, description="The previous page number if available", ge=1
    )
    next_page: int | None = Field(
        None, description="The next page number if available", ge=1
    )

    @classmethod
    def create(
        cls,
        page: int,
        page_size: int,
        total: int,
    ) -> Self:
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1 and total_pages > 0
        next_page = page 7+ 1 if has_next else None
        previous_page = page - 1 if has_previous else None
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            next_page=next_page,
            previous_page=previous_page,
        )


S = TypeVar("S", bound=ResponseSchema)


class PageMixin(ResponseSchema, Generic[S]):
    metadata: PageInfo = Field(..., description="The pagination information")
    data: list[S] = Field(..., description="The list of items on the current page")

    @classmethod
    def create(
        cls,
        *,
        data: list[S],
        page: int,
        page_size: int,
        total: int,
    ) -> Self:
        return cls(
            metadata=PageInfo.create(page=page, page_size=page_size, total=total),
            data=data,
        )


class AuditedQueryParams(RequestSchema):
    created_before: datetime | None = Query(
        default=None,
        description="Filter items created before this date",
    )

    created_after: datetime | None = Query(
        default=None,
        description="Filter items created after this date",
    )

    updated_before: datetime | None = Query(
        default=None,
        description="Filter items updated before this date",
    )

    updated_after: datetime | None = Query(
        default=None,
        description="Filter items updated after this date",
    )


class PageQueryParams(RequestSchema):
    page: PositiveNumber = Query(
        default=1,
        description="The page number to retrieve (1 indexed)",
    )

    page_size: PositiveNumber = Query(
        default=10,
        description="The number of items per page",
    )

    sort_by: str | None = Query(
        default=None,
        description="The field to sort by",
    )

    sort_order: Literal['asc', 'desc'] = Query(
        default="asc",
        description="The order to sort by, either 'asc' or 'desc'",
    )


