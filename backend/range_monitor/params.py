
from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, Query
from pydantic import ConfigDict, Field
from sqlalchemy import Select

from range_monitor.core.dates import UTCDate
from range_monitor.core.pydantic import AliasGenerators, PydanticMixin


class QueryParam(PydanticMixin):
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=AliasGenerators.to_camel_case,
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

class PageParams(QueryParam):
    page_number: PageNumber = 1
    page_size: PageSize = 20

    @property
    def offset(self) -> int:
        return (self.page_number - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

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

    @classmethod
    async def depends(
        cls,
        page_number: PageNumber = Query(default=1),
        page_size: PageSize = Query(default=20),
    ) -> Self:
        return cls(page_number=page_number, page_size=page_size)



class TimestampParams(QueryParam):
    created_before: datetime | None = None
    created_after: datetime | None = None
    updated_before: datetime | None = None
    updated_after: datetime | None = None

    def apply(self, query: Select, col_created, col_updated) -> Select:
        '''
        Applies timestamp filters to a SQLAlchemy Select query.

        Parameters
        ----------
        query : Select
        col_created :
            _The column representing creation timestamps_
        col_updated :
            _The column representing update timestamps_

        Returns
        -------
        Select
            _The query with the parameters_
        '''
        if self.created_before:
            query = query.where(col_created < self.created_before)

        if self.created_after:
            query = query.where(col_created > self.created_after)

        if self.updated_before:
            query = query.where(col_updated < self.updated_before)

        if self.updated_after:
            query = query.where(col_updated > self.updated_after)

        return query

    @classmethod
    async def depends(
        cls,
        created_before: CreatedBefore | None = Query(default=None),
        created_after: CreatedAfter | None = Query(default=None),
        updated_before: UpdatedBefore | None = Query(default=None),
        updated_after: UpdatedAfter | None = Query(default=None),
    ) -> Self:
        return cls(
            created_before=created_before,
            created_after=created_after,
            updated_before=updated_before,
            updated_after=updated_after,
        )

TimestampParamsDep = Annotated[TimestampParams, Depends(TimestampParams.depends)]
PageParamsDep = Annotated[PageParams, Depends(PageParams.depends)]
