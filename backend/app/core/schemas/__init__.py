from datetime import datetime
from typing import Annotated, Any, Generic, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select

from datetime import datetime


def to_camel(string: str) -> str:
    """used in the custom base model as the "alias generator"
    meaning, the model will accept a camel case field name and
    also the python snake case field name
    Arguments:
        string {str} -- the string to convert to camel case
    Returns:
        str -- the string in camel case
    """
    return "".join(
        word.capitalize() if i else word for i, word in enumerate(string.split("_"))
    )


def dt_serializer(dt: datetime) -> str:
    """the standardized format the API returns dates in"""
    return dt.strftime("%Y-%m-%d %H:%M")


class CustomBaseModel(BaseModel):
    """The base model for all app models allowing for standard serialization
    and deserialization of ambiguous types such as datetime, globally allow
    camel case in the body of requests and responses and also allows for
    the use of enums as values in the models
    """

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        from_attributes=True,
        alias_generator=to_camel,
        json_encoders={
            datetime: dt_serializer
        }
    )

    @classmethod
    def to_model(cls, obj_in: Any) -> Self:
        """converts the input object to the model class
        Returns:
            Self -- the type of the inheriting class
        """
        return cls.model_validate(obj_in, from_attributes=True)

    def serialize(self) -> dict:
        """the standard arguments for .model_dump()
        Returns:
            dict
        """

        return self.model_dump(exclude_unset=True, exclude_none=True)


SchemaT = TypeVar("SchemaT", bound=CustomBaseModel)


class StrictModel(CustomBaseModel):
    """a placeholder (mostly) for now for constraints
    on models that should not allow extra fields
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class GenericAPIResponse(CustomBaseModel):
    '''Generic API response model'''
    data: dict[str, Any]
    message: Annotated[str,
                       Field(..., description="The message returned by the API")]


class APIListResponse(CustomBaseModel, Generic[SchemaT]):
    '''Base Model for defining how a list of items returned by the API
    should be presented for the frontend to easily handle
    Arguments:
        Generic {_type_} -- the model type of the items in the list
    '''
    total: Annotated[int,
                     Field(..., description="The total number of items in the list")]
    data: Annotated[list[SchemaT],
                    Field(..., description="The list of items returned by the API")]
    empty: Annotated[bool, Field(..., description="Whether the list is empty")]

    @classmethod
    def from_list(cls, items: list[SchemaT]) -> "Self[SchemaT]":  # type: ignore
        length = len(items)
        return cls(total=length, data=items, empty=length == 0)


class APIRequestModel(StrictModel):
    """The base model for all app request models"""


class APIQueryRequest(StrictModel):
    """base model for all app query request models"""

    skip: Annotated[int, Field(
        0, ge=0, description="The number of records to skip")]
    limit: Annotated[
        int,
        Field(
            50, ge=1, le=1000, description="The maximum items to return in the response"
        ),
    ]

    def apply_to_query(self, stmnt: Select) -> Select:
        """Applies the skip and limit to the given SQLAlchemy Select statement"""
        if self.skip:
            stmnt = stmnt.offset(self.skip)

        if self.limit:
            stmnt = stmnt.limit(self.limit)

        return stmnt


class APIQueryResult(CustomBaseModel):
    """reprents the pagination metadata for a query
    to help the frontend
    """

    total: Annotated[
        int,
        Field(
            ..., ge=0, description="The total number of records from the returned query"
        ),
    ]
    next_skip: Annotated[
        int,
        Field(
            ...,
            ge=0,
            description="The number of records to skip for the next 'page' of the query",
        ),
    ]
    total_pages: Annotated[
        int,
        Field(..., ge=1, description="The number of pages of results from the query"),
    ]
    total_items: Annotated[
        int,
        Field(..., ge=0, description="The total number of items returned in the query"),
    ]

    @classmethod
    def from_params(
        cls, total_returned: int, total_items: int, params: APIQueryRequest
    ) -> "APIQueryResult":
        """uses the query params to create a query result model

        Arguments:
            total_returned {int} -- the total returned from the query results
            params {APIQueryRequest} -- the query params

        Returns:
            APIQueryResult -- the query result model
        """
        return cls(
            total=total_returned,
            next_skip=params.skip + params.limit,
            total_pages=(total_items + params.limit - 1) // params.limit,
            total_items=total_items,
        )


class APIQueryResponse(CustomBaseModel, Generic[SchemaT]):
    '''The base response returned for routes that use query params
    with utility information for the frontend to structure the next
    query and to handle pagination better
    '''
    results: Annotated[
        list[SchemaT],
        Field(..., description="The results of the query of type SchemaT"),
    ]
    page_context: Annotated[
        APIQueryResult,
        Field(
            ..., description="Metadata for the query results for the frontend to handle"
        ),
    ]

    @classmethod
    def from_results(
        cls, db_out: list[SchemaT], query_total: int, query_params: APIQueryRequest
    ) -> Self:
        """given a list of models from the database, the type of the
        pydantic schema to convert them to and the query params for the
        request, returns a query response based on the number of results returned

        Arguments:
            schema_cls {type[SchemaT]} -- _description_
            db_out {list[Any]} -- _description_
            query_params {APIQueryRequest} -- _description_

        Returns:
            APIQueryResponse[SchemaT] -- _description_
        """
        query_meta = APIQueryResult.from_params(
            len(db_out), query_total, query_params)
        return cls(results=db_out, page_context=query_meta)


class AuthForm(StrictModel):
    """The base model for all app authentication forms"""

    username: Annotated[str,
                        Field(..., description="The username of the user")]
    password: Annotated[str,
                        Field(..., description="The password of the user")]
