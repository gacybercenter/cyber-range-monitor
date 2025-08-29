import math
from typing import Annotated, Generic, Self, TypeVar

from pydantic import ConfigDict, Field
from sqlalchemy import Select

from range_monitor.core.dates import UTCDate
from range_monitor.core.pydantic import AliasGenerator, PydanticMixin


class RequestSchema(PydanticMixin):
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=AliasGenerator.to_camel_case,
    )

class ResponseSchema(PydanticMixin):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator.to_camel_case,
    )

# -- page params ---
PageNumber = Annotated[
    int,
    Field(
        ge=1,
        lt=100,
        description='The page number of pages.',
    )
]

PageSize = Annotated[
    int,
    Field(
        ge=1,
        le=100,
        description='The number of items per page',
    )
]
NextPage = Annotated[
    int,
    Field(description='The next page number (null if no next page)'),
]
TotalPages = Annotated[
    int,
    Field(description='The total number of pages available', ge=0),
]
QueryTotal = Annotated[
    int,
    Field(description='The total number of items available', ge=0),
]
# -- timestamp params ---
CreatedBefore = Annotated[
    UTCDate,
    Field(description='Records created before this timestamp'),
]
CreatedAfter = Annotated[
    UTCDate, Field(description='Records created after this timestamp')
]
UpdatedBefore = Annotated[
    UTCDate,
    Field(description='Records updated before this timestamp'),
]
UpdatedAfter = Annotated[
    UTCDate,
    Field(description='Records updated after this timestamp'),
]


class PageParams(RequestSchema):
    page_number: PageNumber = 1
    page_size: PageSize = 20

    @property
    def offset(self) -> int:
        return (self.page_number - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    def paginate(self, query: Select) -> Select:
        return query.offset(self.offset).limit(self.limit)



class TimestampParams(RequestSchema):
    created_before: CreatedBefore | None = None
    created_after: CreatedAfter | None = None
    updated_before: UpdatedBefore | None = None
    updated_after: UpdatedAfter | None = None

    def apply(self, query: Select, col_created, col_updated) -> Select:
        if self.created_before:
            query = query.where(col_created < self.created_before)
        if self.created_after:
            query = query.where(col_created > self.created_after)
        if self.updated_before:
            query = query.where(col_updated < self.updated_before)
        if self.updated_after:
            query = query.where(col_updated > self.updated_after)
        return query


class PageInfo(ResponseSchema):
    number: PageNumber
    size: PageSize
    total_pages: TotalPages
    total: QueryTotal
    next_page: NextPage = -1
    previous_page: NextPage = -1
    has_previous: bool
    has_next: bool

    @classmethod
    def create(
        cls,
        *,
        page_number: int,
        page_size: int,
        total_items: int,
    ) -> Self:
        total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
        has_previous = page_number > 1
        has_next = page_number < total_pages
        next_page = page_number + 1 if has_next else -1
        previous_page = page_number - 1 if has_previous else -1
        return cls(
            number=page_number,
            size=page_size,
            total_pages=total_pages,
            total=total_items,
            next_page=next_page,
            previous_page=previous_page,
            has_previous=has_previous,
            has_next=has_next,
        )


S = TypeVar('S')

class PageSchema(ResponseSchema, Generic[S]):
    data: list[S] = Field(..., description='List of items on the current page')
    page: PageInfo = Field(
        ...,
        description='Information about the current page, including pagination details',
    )

    @classmethod
    def from_results(
        cls,
        *,
        data: list[S],
        page_number: int,
        page_size: int,
        total: int,
    ) -> Self:
        """
        Creates a PageModel instance from the provided data and pagination parameters.

        Parameters
        ----------
        data : list[S]
            The list of items on the current page.
        page_number : int
            The current page number.
        page_size : int
            The number of items per page.
        total_items : int
            The total number of items across all pages.

        Returns
        -------
        PageSchema[S]
            An instance of PageSchema containing the data and pagination info.
        """
        page_info = PageInfo.create(
            page_number=page_number,
            page_size=page_size,
            total_items=total,
        )
        return cls(data=data, page=page_info)