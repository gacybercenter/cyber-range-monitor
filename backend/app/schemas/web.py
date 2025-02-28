from datetime import datetime
from enum import StrEnum
import json
from re import A
from typing import Annotated, Any, Generic, Literal, Optional, Dict, TypeVar
from zoneinfo import ZoneInfo

from sqlalchemy.orm import DeclarativeMeta
from fastapi import Response, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


def datetime_to_iso_format(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
    return dt.isoformat()


DBModel = TypeVar('DBModel', bound=DeclarativeMeta)


class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: datetime_to_iso_format
        },
        populate_by_name=True,
        validate_assignment=True
    )

    @model_validator(mode='before')
    @classmethod
    def ensure_dt_timezone(cls, model_data: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in model_data.items():
            if not isinstance(value, datetime):
                continue
            if not value.tzinfo:
                model_data[key] = value.replace(tzinfo=ZoneInfo('UTC'))
        return model_data

    def serializer(self) -> Dict[str, Any]:
        return jsonable_encoder(self.model_dump(exclude_unset=True))


T = TypeVar('T')


class DatabaseModel(AppBaseModel):
    '''The base for all pydantic models that model an ORM in the database
    Arguments:
        AppBaseModel {_type_} 
    '''
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db(cls, db_model: DeclarativeMeta) -> 'DatabaseModel':
        return cls.model_validate(db_model)

    @classmethod
    def from_db_list(cls, db_models: list[DeclarativeMeta]) -> list['DatabaseModel']:
        return [cls.from_db(db_model) for db_model in db_models]


class APIResponse(AppBaseModel):
    '''The base for all API responses'''
    success: Annotated[bool, Field(
        default=True,
        description='Whether the request was successful'
    )]
    message: Annotated[Optional[str], Field(
        default=None,
        description='A message describing the response'
    )]


class APIDataResponse(APIResponse, Generic[T]):
    '''The base for a response that returns data'''
    data: Annotated[Optional[T], Field(
        default=None,
        description='The data returned by the request'
    )]


class APIListResponse(APIResponse, Generic[T]):
    items: Annotated[Optional[list[T]], Field(
        default=None,
        description='The list of data returned by the request'
    )]
    total: Annotated[int, Field(
        ...,
        description='The total number of items in the list'
    )]


class APIPagedResponse(APIListResponse[T]):
    '''the base for a paged response'''
    page: Annotated[int, Field(
        ...,
        description='The current page number'
    )]
    page_size: Annotated[int, Field(
        default=20,
        description='The number of items per page'
    )]
    pages: Annotated[int, Field(
        ...,
        description='The total number of pages'
    )]

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'success': True,
                'message': 'The request was successful',
                'items': [
                    {
                        'id': 1,
                        'name': 'John Doe'
                    }
                ],
                'total': 1,
                'page': 1,
                'page_size': 20
            }
        }
    )


class APIErrorResponse(APIResponse):
    '''Base error response model

    Arguments:
        Generic[StrEnum] -- a labels for the types of errors 
        that can be returned by a request, 
        (e.g raise HTTPNotFound has a label of 'NOT_FOUND')
    '''
    success: bool = False
    error_label: Annotated[Optional[str], Field(
        default=None,
        description='The error label for the response the frontend can use'
    )]
    message: Annotated[str, Field(
        ...,
        description='The error message describing the response'
    )]

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'success': False,
                'error_label': 'NOT_FOUND',
                'message': 'The requested resource was not found'
            }
        }
    )


class APIRequestBase(AppBaseModel):
    '''Base model for all inbound requests and ensures
    no extra fields are allowed.
    '''
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True
    )


class CookieOptions(BaseModel):
    '''the options for creating a cookie'''
    max_age: Annotated[int, Field(
        default=3600,
        description='The max age of the cookie in seconds'
    )]
    httponly: Annotated[bool, Field(
        default=True,
        description='Whether the cookie is HTTP only'
    )]
    secure: Annotated[bool, Field(
        default=True,
        description='Whether the cookie is secure'
    )]
    samesite: Annotated[Literal['lax', 'strict', 'none'], Field(
        default='lax',
        description='The SameSite attribute of the cookie'
    )]
    path: Annotated[str, Field(
        default='/',
        description='The path of the cookie'
    )] = '/'


class APICookieModel(BaseModel):
    '''represents a reusable configurable cookie 
    that can be set in responses and scanned from a request'''
    options: Annotated[CookieOptions, Field(
        ...,
        description='The options for the cookie'
    )]
    name: Annotated[str, Field(
        ...,
        description='The name of the cookie'
    )]

    def set_cookie(self, response: Response, data: str) -> None:
        '''given a response and data, the cookie is set

        Arguments:
            response {Response} -- _description_
            data {AppBaseModel | str} -- _description_
        '''
        options = self.options.model_dump(exclude_unset=True)
        response.set_cookie(
            key=self.name,
            value=data,
            **options
        )

    def scan_request(self, request: Request) -> Optional[str]:
        '''scans the request for the cookie'''
        return request.cookies.get(self.name)


FormUsername = Annotated[str, StringConstraints(
    min_length=3,
    max_length=50,
    pattern=r'^[a-zA-Z0-9_.-]+$'
)]

FormPassword = Annotated[str, StringConstraints(
    min_length=3,
    max_length=128
)]


class AuthForm(APIRequestBase):
    '''the constraints on inputs from the auth forms
    '''
    username: Annotated[FormUsername, Field(
        ...,
        description='The username of the user (min length = 3, max length = 50)'
    )]
    password: Annotated[FormPassword, Field(
        ...,
        description='The password of the user (min length = 3, max length = 128)'
    )]
