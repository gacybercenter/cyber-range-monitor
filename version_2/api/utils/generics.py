from pydantic import BaseModel, Field


# Generic Pydantic Models for the API

class BaseQueryParam(BaseModel):
    '''
    Standard query parameters for any route that supports
    query parameters 
    Arguments:
        BaseModel {_type_} -- _description_
    '''
    skip: int = Field(
        0, ge=0, description="The number of records to skip"
    )
    limit: int = Field(
        50, ge=1, le=1000, description="The number of records to return"
    )
    sort_order: str = Field(
        "asc", description="The order to sort the records by"
    )


class QueryMetaResult(BaseModel):
    '''
    Information for the frontend on how to handle the results of a query
    and to build the next request for a given query.
    '''
    total: int = Field(
        ..., ge=0, description="The total number of records from the returned query"
    )
    next_skip: int = Field(..., ge=0,
                           description="The number of records to skip for the next 'page' of the query")
    num_page: int = Field(..., ge=1,
                          description="The number of pages of results from the query")

    @classmethod
    def init(cls, total: int, skip: int, limit: int) -> 'QueryMetaResult':
        return cls(
            total=total,
            next_skip=skip + limit,
            num_page=(total + limit - 1) // limit
        )


class ResponseMessage(BaseModel):
    message: str = Field(..., description="A message to return to the client")


class QueryResponse(BaseModel):
    meta: QueryMetaResult = Field(..., description="Metadata for the query results for the frontend to handle")
    result: list[BaseModel] = Field(..., description="The results of the query")
