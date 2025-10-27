from typing import Any

import httpx
import msgspec

from server.utils.decorators.retries import retry_request


@retry_request()
async def get_json(path: str, client: httpx.AsyncClient) -> dict | Any:
    response = await client.get(path)
    response.raise_for_status()
    return response.json()


@retry_request()
async def stream_get_json(path: str, client: httpx.AsyncClient) -> dict | Any:
    '''
    33% better performance on larger responses, not a robust or comprehensive
    streaming implementation by any means. For more robust streaming, consider
    implementing a custom json parser for msgspec

    Parameters
    ----------
    path : str
        The URL path to fetch JSON from.
    client : httpx.AsyncClient
        The HTTPX async client to use for the request.

    Returns
    -------
    dict | Any
    '''
    async with client.stream('GET', path) as response:
        response.raise_for_status()

        json_buffer = bytearray()
        async for chunk in response.aiter_bytes():
            json_buffer.extend(chunk)

    return msgspec.json.decode(json_buffer)


async def fetch_json(
    path: str, client: httpx.AsyncClient, *, stream: bool = False
) -> dict | Any:
    if stream:
        return await stream_get_json(path, client)

    return await get_json(path, client)


async def fetch_json_stream(  # noqa: ANN201, D417
    client: httpx.AsyncClient,
    url: str,
    *,
    read_timeout: float = 60.0,
    headers: dict | None = None,
):
    '''
    Streams JSON data from the given URL using the provided HTTPX async client.

    Parameters
    ----------
    client : httpx.AsyncClient
    url : str
    read_timeout : float, optional, by default 60.0
    headers : dict | None, optional by default None

    Yields
    ------
    bytes
    '''
    timeout = httpx.Timeout(10.0, read=read_timeout, write=10.0, connect=5.0)

    async with client.stream('GET', url, headers=headers, timeout=timeout) as response:
        response.raise_for_status()
        async for chunk in response.aiter_bytes():
            yield chunk
