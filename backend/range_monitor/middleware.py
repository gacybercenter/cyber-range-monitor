from __future__ import annotations

import dataclasses
import time
import uuid
from collections.abc import Callable
from http import HTTPStatus
from typing import Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from range_monitor import log
from range_monitor.core.request_parse import (
    RequestAuditor,
    RequestRecord,
    ResponseRecord,
)


class AccessAuditor:

    @staticmethod
    async def audit_request(request: Request) -> RequestRecord:
        """
        Creates a request record and structured log entry for the incoming request.

        Parameters
        ----------
        request : Request

        Returns
        -------
        RequestRecord
        """
        record = RequestAuditor.parse_request(request)
        message = (
            f'Incoming ({record.method}) request to {record.url} from client '
            f'{record.ip_address} {record.user_agent.browser} / {record.user_agent.os}.'
        )

        log.create_access_log(message=message, **dataclasses.asdict(record))
        return record

    @staticmethod
    async def audit_response(
        req_record: RequestRecord,
        response: Response,
        start_time: float
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
        record = RequestAuditor.parse_response(
            response=response,
            req_start=start_time
        )

        phrase = HTTPStatus(record.status_code).phrase
        message = (
            f'Responded to Request {req_record.id} in {record.elapsed:.3f}s with a '
            f'{record.status_code}, {phrase} to client: {req_record.ip_address} '
            f'{req_record.user_agent.browser} / {req_record.user_agent.os}.'
        )

        log.create_access_log(message=message, **dataclasses.asdict(record))
        return record




class AccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)


    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        request_record = await AccessAuditor.audit_request(request)

        response = await call_next(request)
        await AccessAuditor.audit_response(
            req_record=request_record,
            response=response,
            start_time=start_time,
        )
        return response


def correlation_id_generator() -> str:
    return uuid.uuid4().hex