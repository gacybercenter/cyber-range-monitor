import math
from typing import Annotated, Generic, TypeVar

from pydantic import ConfigDict, Field

from range_monitor.core.schema import AliasGenerator, PydanticMixin


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

PageNumber = Annotated[
    int,
    Field(
        ge=1,
        description='The current page number',
    ),
]
PageSize = Annotated[
    int,
    Field(
        ge=0,
        description='The number of items per page',
    ),
]


class PageDetails(ResponseModel):
    number: PageNumber
    size: PageNumber
    total_pages: TotalPages
    total: QueryTotal
    next_page: NextPage = -1
    previous_page: NextPage = -1


S = TypeVar('S')


class PageModel(ResponseModel, Generic[S]):
    data: list[S] = Field(..., description='List of items on the current page')
    page: PageDetails = Field(
        ...,
        description='Information about the current page, including pagination details',
    )

    @staticmethod
    def get_page_details(
        page_number: int,
        page_size: int,
        total_items: int,
    ) -> PageDetails:
        total_pages = math.ceil(
            total_items / page_size) if page_size > 0 else 0
        next_page = page_number + 1 if page_number < total_pages else -1
        previous_page = page_number - 1 if page_number > 1 else -1

        return PageDetails(
            number=page_number,
            size=page_size,
            total_pages=total_pages,
            total=total_items,
            next_page=next_page,
            previous_page=previous_page
        )
