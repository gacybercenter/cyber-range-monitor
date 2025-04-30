import functools
from operator import methodcaller
from typing import (
    Callable,
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    Set,
    TypeVar,
    Sequence
)
from fastapi import FastAPI, APIRouter, Response, Depends, dependencies
from enum import StrEnum

from fastapi.datastructures import Default
from fastapi.routing import APIRoute

# NOTE: This file helps for creating the OpenAPI spec for the backend and may seem
# like a lot of boilerplate but it helps when creating axios client from the OpenAPI spec
# because without it, the service names created for the routes are verbose (e.g "eventLogReadSummaryGetGet")
# to eventLogs.getSummary()
# From Official Documentation: https://fastapi.tiangolo.com/advanced/generate-clients/#client-method-names


def create_operation_id(route: APIRoute) -> str:
    '''Generates a unique id for the route to help normalize
    the API service names.
    https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function
    Returns:
        str -- the adjusted operation ID
    '''
    return f"{route.tags[0]}-{route.name}"


# Type variable for return type
T = TypeVar('T')
DecoratedCallable = TypeVar('DecoratedCallable', bound=Callable[..., Any])


class annotated_route:
    '''class decorator to add metadata a method to be used as a route

    NOTE: this isn't creating a real route but rather a decorator which 
    cabn be used to add metadata to a function which can be used later
    '''

    def __init__(
        self,
        path: str,
        *,
        response_model: Type[Any],
        status_code: Optional[int] = 200,
        tags: Optional[List[str]] = None,
        dependencies: Optional[Sequence] = None,
        methods: Optional[Sequence[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict] = None,
        operation_id: Optional[str] = None,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Optional[Type[Response]] = None,
        name: Optional[str] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ):
        self.path: str = path
        self.method = methods or ['GET']
        self.kwargs: Dict[str, Any] = {
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags or [],
            "dependencies": dependencies or [],
            "summary": summary,
            "description": description,
            "response_description": response_description,
            "responses": responses or {},
            "methods": self.method,
            "operation_id": operation_id,
            "response_model_exclude_none": response_model_exclude_none,
            "include_in_schema": include_in_schema,
            "response_class": response_class,
            "name": name,
            "openapi_extra": openapi_extra,
        }

    def __call__(self, func: DecoratedCallable) -> DecoratedCallable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Add route metadata to the function
        setattr(wrapper, "__route_path__", self.path)
        setattr(wrapper, "__route_kwargs__", self.kwargs)
        return wrapper  # type: ignore


def register_route_annotations(
    annotated_class: Any,
    router: APIRouter
) -> None:

    for attr_name in dir(annotated_class):
        if attr_name.startswith("__"):
            continue

        method = getattr(annotated_class, attr_name)
        if not hasattr(method, "__route_path__") or not hasattr(method, "__route_kwargs__"):
            continue

        path = method.__route_path__
        route_init = method.__route_kwargs__
        router.add_api_route(
            path=path,
            endpoint=method,
            **route_init
        )
