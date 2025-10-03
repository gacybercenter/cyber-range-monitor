import asyncio
import dataclasses as dc
import functools
import random
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import httpcore
import httpx

P = ParamSpec("P")
R = TypeVar("R")


class NoAttemptsLeftError(Exception):
    '''
    When no attempts are left to retry a request.
    '''


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
    httpcore.ConnectError,
)

@dc.dataclass(slots=True)
class RetryPolicy:
    '''
    Parameters
    ----------
    attempts : int, optional
        The maximum number of attempts, by default 3
    delay : float, optional
        The base delay between attempts, by default 0.25
    jitter : float, optional
        The jitter factor to apply to the delay, by default 0.1
    '''
    attempts: int = 3
    delay: float = 0.25
    jitter: float = 0.1

    def get_timeout(self, attempt_no: int) -> float:
        base = self.delay * attempt_no

        if self.jitter:
            j = base * self.jitter
            base += random.uniform(-j, j)

        return max(0.0, base)


    def __call__(
        self,
        func: Callable[P, Awaitable[R]],
        *args,
        **kwargs
    ) -> Callable[P, Awaitable[R]]:

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await self.call_with_retries(func, *args, **kwargs)

        return wrapper

    async def call_with_retries(
        self,
        func: Callable[P, Awaitable[R]],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> R:
        httpx_errors = _HTTPX_ERRORS
        last_exc: BaseException | None = None
        for attempt_no in range(1, self.attempts + 1):
            try:
                return await func(*args, **kwargs)
            except httpx_errors as exc:
                last_exc = exc
                if attempt_no == self.attempts:
                    break
                timeout = self.get_timeout(attempt_no)
                await asyncio.sleep(timeout)
            except Exception:
                raise

        raise NoAttemptsLeftError(
            f"Failed after {self.attempts} attempts: {last_exc}"
        ) from last_exc


def retry_request(policy: RetryPolicy | None = None) :
    '''
    A decorator to apply retry logic to async HTTPX request methods.

    Parameters
    ----------
    policy : RetryPolicy | None, optional
        The retry policy to use, by default None

    Returns
    -------
    Callable
    '''
    policy = policy or RetryPolicy()

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await policy.call_with_retries(func, *args, **kwargs)

        return wrapper

    return decorator