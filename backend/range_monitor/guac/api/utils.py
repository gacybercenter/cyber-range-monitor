from typing import Any

import httpx
import msgspec

from range_monitor.utils.decorators import retry_request


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
    client : httpx.AsyncClient

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


async def fetch(
    path: str,
    client: httpx.AsyncClient,
    *,
    stream: bool = False
) -> dict | Any:
    if stream:
        return await stream_get_json(path, client)

    return await get_json(path, client)