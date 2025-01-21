from pydantic import BaseModel, Field
from typing import Optional


class BaseQueryParam(BaseModel):
    skip: int = Field(0, ge=0, description="The number of records to skip")
    limit: int = Field(50, ge=1, le=1000, description="The number of records to return")
    sort_order: str = Field("asc", description="The order to sort the records by")

class QueryMetaResult(BaseModel):
    total: int
    next_skip: int
    num_page: int

    @classmethod
    def init(cls, total: int, skip: int, limit: int) -> 'QueryMetaResult':
        return cls(
            total=total,
            next_skip=skip + limit,
            num_page=(total + limit - 1) // limit
        )


class QueryResponse(BaseModel):
    meta: QueryMetaResult
    result: list[BaseModel]
