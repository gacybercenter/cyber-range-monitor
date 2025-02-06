from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, Strict
from sqlalchemy import Select


# Generic Pydantic Models for the API

class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid'
    )
    


class QueryFilters(StrictModel):
    '''
    Standard query parameters for any route that supports
    query parameters 
    Arguments:
        BaseModel {_type_} -- _description_
    '''
    skip: Optional[int] = Field(
        0, ge=0, description="The number of records to skip"
    )
    limit: Optional[int] = Field(
        50, ge=1, le=1000, description="The number of records to return"
    )
    
    
    def apply_to_stmnt(self, stmnt: Select) -> Select:
        if self.skip:
            stmnt = stmnt.offset(self.skip)
        if self.limit:
            stmnt = stmnt.limit(self.limit)
        return stmnt
        


class QueryResultData(StrictModel):
    '''
    Information for the frontend on how to handle the results of a query
    and to build the next request for a given query.
    '''
    total: int = Field(
        ...,
        ge=0,
        description="The total number of records from the returned query"
    )
    
    next_skip: int = Field(
        ...,
        ge=0,
        description="The number of records to skip for the next 'page' of the query"
    )
    
    num_page: int = Field(
        ...,
        ge=1,
        description="The number of pages of results from the query"
    )

    @classmethod
    def init(cls, total: int, skip: int, limit: int) -> 'QueryResultData':
        return cls(
            total=total,
            next_skip=skip + limit,
            num_page=(total + limit - 1) // limit
        )


class ResponseMessage(BaseModel):
    message: str = Field(..., description="A message to return to the client")


class QueryResponse(BaseModel):
    meta: QueryResultData = Field(
        ..., 
        description="Metadata for the query results for the frontend to handle"
    )
    result: list[BaseModel] = Field(
        ...,
        description="The results of the query"
    )

    
    
    
    
    