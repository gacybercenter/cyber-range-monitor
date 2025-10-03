from typing import Annotated

from fastapi import Depends, Query
from pydantic import ConfigDict, Field
from sqlalchemy import Select

from range_monitor.core.schema import AliasGenerator, PydanticMixin


class QueryParam(PydanticMixin):
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=AliasGenerator.to_camel_case,
    )


PageNumber = Annotated[
    int,
    Field(
        ge=1,
        lt=100,
        description='The page number of pages.',
    ),
]

PageSize = Annotated[
    int,
    Field(
        ge=1,
        le=100,
        description='The number of items per page',
    ),
]


class PageParams(QueryParam):
    page_number: PageNumber = 1
    page_size: PageSize = 20

    @property
    def offset(self) -> int:
        real = (self.page_number - 1) * self.page_size
        return max(real, 0)

    @property
    def limit(self) -> int:
        return max(self.page_size, 1)

    def paginate(self, query: Select) -> Select:
        '''
        Applies pagination to a SQLAlchemy Select query.

        Parameters
        ----------
        query : Select
            _The statement to paginate_

        Returns
        -------
        Select
            _The paginated query_
        '''
        return query.offset(self.offset).limit(self.limit)


async def get_page_params(
    page_number: PageNumber = Query(default=1),
    page_size: PageSize = Query(default=20),
) -> PageParams:
    return PageParams(
        page_number=page_number,
        page_size=page_size
    )

PageParamsDep = Annotated[PageParams, Depends(get_page_params)]
