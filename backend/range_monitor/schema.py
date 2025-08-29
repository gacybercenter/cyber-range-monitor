'''
Utility schemas used for request and response models.
'''
import math
from typing import Annotated, Generic, Self, TypeVar

from pydantic import ConfigDict, Field

from range_monitor.core.pydantic import AliasGenerator, PydanticMixin


class RequestBody(PydanticMixin):
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=AliasGenerator.to_camel_case,
    )

class ResponseModel(PydanticMixin):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator.to_camel_case,
    )

# -- page params ---
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


class PageInfo(ResponseModel):
    number: int = Field(..., description='The current page number', ge=1)
    size: int = Field(..., description='The number of items per page', ge=0)
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

class PaginatedList(ResponseModel, Generic[S]):
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