import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from starlette.concurrency import run_in_threadpool as starlette_run_in_threadpool

R = TypeVar('R')
P = ParamSpec('P')


def asyncify() -> Callable[[Callable[P, R]], Callable[P, Awaitable[R]]]:
    """
    Decorator that makes a blocking sync function async by
    running it in a threadpool.

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, Awaitable[R]]]
    """

    def decorator(func: Callable[P, R]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await starlette_run_in_threadpool(func, *args, **kwargs)

        return wrapper

    return decorator
