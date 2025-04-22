

from typing import Callable, Awaitable

from fastapi import Request, Response


type CallNext = Callable[[Request], Awaitable[Response]]
