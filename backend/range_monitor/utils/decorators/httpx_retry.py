import asyncio
import dataclasses as dc
import functools
import random
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import httpcore
import httpx

from range_monitor.errors import GatewayTimeout

P = ParamSpec("P")
R = TypeVar("R")


class NoAttemptsLeftError(GatewayTimeout):
    """Raised when no retry attempts are left - 504"""


_HTTPX_ERRORS = (
    ConnectionError,
    asyncio.TimeoutError,
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.WriteError,
    httpx.RemoteProtocolError,
    httpx.PoolTimeout,
    httpx.ProxyError,
    httpx.NetworkError,
    httpcore.ConnectError
)


@dc.dataclass(slots=True)
class RetryPolicy:
    attempts: int = 3
    delay: float = 0.25
    jitter: float = 0.1

    def get_timeout(self, attempt_no: int) -> float:
        base = self.delay * attempt_no
        if self.jitter:
            j = base * self.jitter
            base += random.uniform(-j, j)
        return max(0.0, base)



async def call_with_retries(
    func: Callable[P, Awaitable[R]],
    policy: RetryPolicy,
    *args: P.args,
    **kwargs: P.kwargs
) -> R:
    '''
    Calls an async function with retries according to the given policy.

    Parameters
    ----------
    func : Callable[P, Awaitable[R]]
    policy : RetryPolicy

    Returns
    -------
    R

    Raises
    ------
    NoAttemptsLeftError
    '''
    httpx_errors = _HTTPX_ERRORS
    last_exc: BaseException | None = None

    for attempt_no in range(1, policy.attempts + 1):
        try:
            return await func(*args, **kwargs)
        except httpx_errors as exc:
            last_exc = exc
            if attempt_no == policy.attempts:
                break
            timeout = policy.get_timeout(attempt_no)
            await asyncio.sleep(timeout)
        except Exception:
            raise

    raise NoAttemptsLeftError(
        f"Failed after {policy.attempts} attempts: {last_exc}"
    ) from last_exc


def retry_request(
    policy: RetryPolicy | None = None
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    '''
    Adds basic retry logic to an async function that makes HTTP requests
    using httpx. Do not use this on requests that should be retried


    Parameters
    ----------
    policy : RetryPolicy | None, optional
        Retry policy to use, by default None which uses the default
        parameters of RetryPolicy.

    Returns
    -------
    Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]
    '''
    policy = policy or RetryPolicy()

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await call_with_retries(func, policy, *args, **kwargs)
        return wrapper

    return decorator
