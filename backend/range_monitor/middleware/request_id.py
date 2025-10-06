from __future__ import annotations

from typing import TYPE_CHECKING

from range_monitor.core import correlation_id

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send

class RequestIdMiddleware:
    '''
    Lower-level ASGI middleware to manage `X-Request-ID` headers
    without the need for an additional package
    '''
    __slots__ = ("app", "header_name")

    def __init__(self, app: 'ASGIApp', header_name: bytes = b"x-request-id") -> None:
        self.app = app
        self.header_name = header_name.lower()

    async def __call__(self, scope: 'Scope', receive: 'Receive', send: 'Send') -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        headers = scope.get("headers", ())

        raw_id = next(
            (
                v for k, v in headers if k.lower() == self.header_name
            ),
            None,
        )
        request_id = (
            raw_id.decode("ascii", "ignore") if raw_id
            else correlation_id.generate()
        )

        token = correlation_id.set_id(request_id)

        async def send_wrapper(message: 'Message') -> None:
            if message["type"] == "http.response.start":
                hdrs = message.setdefault("headers", [])
                hdrs.append((self.header_name, request_id.encode("ascii")))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            correlation_id.reset(token)
