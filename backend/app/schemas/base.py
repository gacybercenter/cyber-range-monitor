from datetime import datetime
from typing import Any, Generic, Optional, Annotated, Self, TypeVar
from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)
from sqlalchemy import Select
from .utils import dt_serializer, to_camel


class CustomBaseModel(BaseModel):
    '''The base model for all app models

    Arguments:
        BaseModel {_type_} -- _description_
    '''
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        from_attributes=True,
        alias_generator=to_camel,
        json_encoders={
            datetime: dt_serializer,
            bytes: lambda v: v.decode(),
        },
    )

    @classmethod
    def to_model(cls, obj_in: Any) -> Self:
        '''converts the input object to the model class 

        Returns:
            Self -- the type of the inheriting class
        '''
        return cls.model_validate(obj_in, from_attributes=True)

    def serialize(self) -> dict:
        '''the standard arguments for .model_dump()

        Returns: 
            dict
        '''

        return self.model_dump(
            exclude_unset=True,
            exclude_none=True
        )


class StrictModel(CustomBaseModel):
    """a placeholder (mostly) for now for constraints
    on models that should not allow extra fields
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class APIResponse(CustomBaseModel):
    data: Optional[Any]
    message: Annotated[str, Field(
        ...,
        description="The message returned by the API"
    )]


class APIRequestModel(StrictModel):
    '''The base model for all app request models'''


class APIQueryRequest(StrictModel):
    '''base model for all app query request models

    Arguments:
        StrictModel {_type_}
    '''
    skip: Annotated[int, Field(
        0,
        ge=0,
        description="The number of records to skip"
    )]
    limit: Annotated[int, Field(
        50,
        ge=1,
        le=1000,
        description="The maximum items to return in the response"
    )]

    def apply_to_query(self, stmnt: Select) -> Select:
        """Applies the skip and limit to the given SQLAlchemy Select statement"""
        if self.skip:
            stmnt = stmnt.offset(self.skip)

        if self.limit:
            stmnt = stmnt.limit(self.limit)

        return stmnt


class APIQueryResult(CustomBaseModel):
    '''reprents the pagination metadata for a query
    to help the frontend
    '''
    total: Annotated[int, Field(
        ...,
        ge=0,
        description="The total number of records from the returned query"
    )]
    next_skip: Annotated[int, Field(
        ...,
        ge=0,
        description="The number of records to skip for the next 'page' of the query"
    )]
    total_pages: Annotated[int, Field(
        ...,
        ge=1,
        description="The number of pages of results from the query"
    )]
    total_items: Annotated[int, Field(
        ...,
        ge=0,
        description="The total number of items returned in the query"
    )]

    @classmethod
    def from_params(cls, total_returned: int, total_items: int, params: APIQueryRequest) -> "APIQueryResult":
        '''uses the query params to create a query result model

        Arguments:
            total_returned {int} -- the total returned from the query results
            params {APIQueryRequest} -- the query params

        Returns:
            APIQueryResult -- the query result model
        '''
        return cls(
            total=total_returned,
            next_skip=params.skip + params.limit,
            total_pages=(total_items + params.limit - 1) // params.limit,
            total_items=total_items
        )


SchemaT = TypeVar('SchemaT', bound=CustomBaseModel)


class APIQueryResponse(CustomBaseModel, Generic[SchemaT]):
    results: Annotated[list[SchemaT], Field(
        ...,
        description="The results of the query of type SchemaT"
    )]
    page_context: Annotated[APIQueryResult, Field(
        ...,
        description="Metadata for the query results for the frontend to handle"
    )]

    
    @classmethod
    def from_results(
        cls,
        db_out: list[SchemaT],
        query_total: int,
        query_params: APIQueryRequest
    ) -> Self:
        '''given a list of models from the database, the type of the 
        pydantic schema to convert them to and the query params for the 
        request, returns a query response based on the number of results returned

        Arguments:
            schema_cls {type[SchemaT]} -- _description_
            db_out {list[Any]} -- _description_
            query_params {APIQueryRequest} -- _description_

        Returns:
            APIQueryResponse[SchemaT] -- _description_
        '''
        query_meta = APIQueryResult.from_params(
            len(db_out),
            query_total,
            query_params
        )
        return cls(
            results=db_out,
            page_context=query_meta
        )
        
class AuthForm(StrictModel):
    '''The base model for all app authentication forms'''
    username: Annotated[str, Field(
        ...,
        description="The username of the user"
    )]
    password: Annotated[str, Field(
        ...,
        description="The password of the user"
    )]
