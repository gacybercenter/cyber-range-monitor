import math
from typing import Annotated, Any

from pydantic import ConfigDict, Field

from server.schema import PydanticModel, to_camel_case


class RequestBody(PydanticModel):
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=to_camel_case,
    )


class ResponseModel(PydanticModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel_case,
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


class PageModel[S](ResponseModel):
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
        total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
        next_page = page_number + 1 if page_number < total_pages else -1
        previous_page = page_number - 1 if page_number > 1 else -1

        return PageDetails(
            number=page_number,
            size=page_size,
            total_pages=total_pages,
            total=total_items,
            next_page=next_page,
            previous_page=previous_page,
        )


ErrorType = Annotated[
    str,
    Field(description='A string representing the type of error that occurred'),
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


class ErrorResponse(PydanticModel):
    """
    The response schema for errors
    """

    model_config = ConfigDict(
        extra='forbid',
        alias_generator=to_camel_case,
    )

    error_type: ErrorType = 'about:blank'
    status: ErrorStatus
    detail: ErrorDetail | None = None
    request_id: ErrorInstance | None = None
    code: ErrorCode | None = None
    extras: ErrorExtras | None = None
