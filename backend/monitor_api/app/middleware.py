from __future__ import annotations

import dataclasses
import time
import uuid
from http import HTTPStatus
from typing import TYPE_CHECKING

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from monitor_api.core import constant, settings
from monitor_api.infra import APILogger
from monitor_api.utils.request_parse import (
    RequestRecord,
    RequestTelemetry,
    ResponseRecord,
)

if TYPE_CHECKING:
    from fastapi import FastAPI, Request, Response


def get_logger():
    return APILogger.bind(name='access')


async def create_request_record(request: Request) -> RequestRecord:
    """
    Creates a request record and structured log entry for the incoming request.

    Parameters
    ----------
    request : Request

    Returns
    -------
    RequestRecord
    """
    record = RequestTelemetry.audit_request(request)
    message = (
        f'Incoming ({record.method}) request to {record.url} from client '
        f'{record.ip_address} {record.user_agent.browser} / {record.user_agent.os}.'
    )

    get_logger().log('SECURITY', message, **dataclasses.asdict(record))
    return record


async def create_response_record(
    req_record: RequestRecord, response: Response, start_time: float
) -> ResponseRecord:
    """
    Creates a response record and structured log entry for the response.

    Parameters
    ----------
    req_record : RequestRecord
    response : Response
    start_time : float

    Returns
    -------
    ResponseRecord
    """
    record = RequestTelemetry.audit_response(
        response=response,
        req_start=start_time,
    )

    phrase = HTTPStatus(record.status_code).phrase
    message = (
        f'Responded to Request {req_record.id} in {record.elapsed:.3f}s with a '
        f'{record.status_code}, {phrase} to client: {req_record.ip_address} '
        f'{req_record.user_agent.browser} / {req_record.user_agent.os}.'
    )

    get_logger().log('SECURITY', message, **dataclasses.asdict(record))
    return record

async def access_middleware(request: Request, call_next) -> Response:
    '''
    Middleware to log incoming requests and outgoing responses including
    performance metrics.

    Parameters
    ----------
    request : Request
    call_next : _The next middleware_

    Returns
    -------
    Response
    '''
    start_time = time.perf_counter()
    req_record = await create_request_record(request)
    request.state.metadata = req_record
    response = await call_next(request)
    await create_response_record(
        req_record=req_record,
        response=response,
        start_time=start_time,
    )
    return response


class AccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, dispatch=access_middleware)

def request_id_maker() -> str:
    return uuid.uuid4().hex


def mount_middleware(app: 'FastAPI') -> None:
    '''
    Registers necessary middleware to the FastAPI app.

    Parameters
    ----------
    app : FastAPI
    '''
    env_settings = settings.get_env_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=env_settings.CORS_ALLOW_ORIGINS,
        allow_credentials=env_settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=env_settings.CORS_ALLOW_METHODS,
        allow_headers=env_settings.CORS_ALLOW_HEADERS,
    )
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name=constant.REQUEST_ID_HEADER_NAME,
        update_request_header=True,
        generator=request_id_maker,
    )
    app.add_middleware(AccessMiddleware)