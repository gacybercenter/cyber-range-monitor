
from typing import Annotated, Any, Generic, List, Self, TypeVar
from pydantic import ConfigDict, Field, PositiveInt
from sqlalchemy import Select

from .base import CustomBaseModel


class RequestSchema(CustomBaseModel):
    '''The base request schema for all API requests'''
    model_config = ConfigDict(
        extra='forbid',
        strict=True
    )


class ResponseSchema(CustomBaseModel):
    '''the base response schema for all API responses'''


ResponseT = TypeVar('ResponseT', bound='ResponseSchema')
RequestT = TypeVar('RequestT', bound=RequestSchema)


class ResponseList(ResponseSchema, Generic[ResponseT]):
    size: Annotated[int, Field(
        ...,
        description="The total number of items in the list"
    )]

    is_empty: Annotated[bool, Field(
        ...,
        description="Whether the list is empty"
    )]

    data: Annotated[list[Any], Field(
        ...,
        description="The list of items returned by the API"
    )]

    @classmethod
    def from_results(cls, data: list[ResponseT]) -> 'Self':
        items = len(data)
        is_empty = items == 0
        return cls(
            size=items,
            is_empty=is_empty,
            data=data
        )


class MessagedResponse(CustomBaseModel):
    '''Generic API response model'''
    data: Annotated[Any, Field(
        None,
        description="Optional additional data to include"
    )]
    message: Annotated[str, Field(
        ...,
        description="The message returned by the API"
    )]


class PagedQueryParameters(RequestSchema):
    page: Annotated[PositiveInt, Field(
        ...,
        ge=1,
        description="The page number to get"
    )]
    page_size: Annotated[PositiveInt, Field(
        ...,
        ge=1,
        le=100,
        description="The number of items per page"
    )]

    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def apply_to_query(self, stmnt: Select) -> Select:
        """Applies the page and page size to the given SQLAlchemy Select statement"""
        if self.page_size:
            stmnt = stmnt.limit(self.page_size)

        if self.page:
            stmnt = stmnt.offset(self.offset())

        return stmnt


class PageData(ResponseSchema):
    '''Meta data for paginated responses'''
    total: Annotated[int, Field(
        ...,
        description="The total number of items in the list"
    )]

    is_empty: Annotated[bool, Field(
        ...,
        description="Whether the list is empty"
    )]

    total_pages: Annotated[int, Field(
        ...,
        description="The total number of pages in the list"
    )]

    page_size: Annotated[int, Field(
        ...,
        description="The number of items per page"
    )]

    has_next: Annotated[bool, Field(
        ...,
        description="Whether there are more pages available"
    )]

    has_previous: Annotated[bool, Field(
        ...,
        description="Whether there are previous pages available"
    )]

    @classmethod
    def from_results(
        cls,
        items: List[Any],
        total_count: int,
        page: int = 1,
        page_size: int | None = None
    ) -> Self:
        '''Creates the meta data for a paginated response easy for frontend 
        to resolve. 

        Args:
            items (List[Any]): _the items on the current page_
            total_count (int): _the total number of items returned_
            page (int, optional): _the current page_. Defaults to 1.
            page_size (int | None, optional): _the page size_. Defaults to None.

        Returns:
            Self: _the page data_
        '''
        item_count = len(items)
        page_size = item_count if not page_size else page_size

        if page_size <= 0:
            total_pages = 0
        else:
            total_pages = (total_count + page_size - 1) // page_size

        is_empty = item_count == 0
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            total=total_count,
            is_empty=is_empty,
            total_pages=total_pages,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )


class PagedResponse(CustomBaseModel, Generic[ResponseT]):
    '''Paginated response model for API responses'''
    data: Annotated[list[ResponseT] | Any, Field(
        ..., description="The list of items returned by the API"
    )]
    page_metadata: Annotated[PageData, Field(
        ...,
        description="The metadata for the paginated response"
    )]

    @classmethod
    def from_request_results(
        cls,
        items: list[ResponseT],
        total_count: int,
        page_number: int = 1,
        page_size: int | None = None
    ) -> Self:
        """Creates a paginated response from the given items and total items count"""
        metadata = PageData.from_results(
            items=items,
            total_count=total_count,
            page=page_number,
            page_size=page_size
        )
        return cls(
            data=items,
            page_metadata=metadata
        )
