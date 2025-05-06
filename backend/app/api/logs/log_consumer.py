import asyncio
import contextlib
import logging
from typing import Any, AsyncGenerator
import redis.asyncio as aioredis
from redis.asyncio.client import PubSub
import queue

from pydantic import BaseModel


logger = logging.getLogger(__name__)


def get_client_backlog(client_id: str) -> str:
    return f'logs:{client_id}:backlog'


def get_client_channel(client_id: str) -> str:
    return f'logs:{client_id}:live'


class ClientKeys:
    __slots__ = ('backlog', 'channel')

    def __init__(self, client_id: str) -> None:
        self.backlog: str = get_client_backlog(client_id)
        self.channel: str = get_client_channel(client_id)


class RedisLogConsumer:

    def __init__(
        self,
        *,
        std_queue: queue.Queue,
        redis: aioredis.Redis,
        client_id: str,
        max_len: int = 1000,
    ) -> None:
        self._queue: queue.Queue[BaseModel] = std_queue
        self._redis: aioredis.Redis = redis
        self._max_len = max_len
        self._keys = ClientKeys(
            client_id=client_id
        )
        self._task: asyncio.Task | None = None

    async def listener(self) -> AsyncGenerator[Any, None]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._keys.channel) # type: ignore
        try:
            async for message in pubsub.listen():
                yield message
        except asyncio.CancelledError:
            logger.info(
                f'The log consumer was cancelled on channel {self._keys.channel}'
            )
        finally:
            await pubsub.unsubscribe(self._keys.channel)
    
    async def get_backlog(self) -> Any:
        return await self._redis.lrange(
            name=self._keys.backlog,
            start=0,
            end=-1
        ) # type: ignore
        
        
        
        
    def start(self) -> None:
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._consumer_loop())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None

    async def _consumer_loop(self) -> None:
        try:
            while True:
                entry = await asyncio.to_thread(self._queue.get)
                data = entry.model_dump_json(exclude_none=True)
                await self._to_redis(data)
        except asyncio.CancelledError:
            logger.info(
                f'The log consumer was cancelled on channel {self._keys.channel}')
        except Exception as e:
            logger.exception(
                f'An error occurred in the log consumer', exc_info=e)

    async def _to_redis(self, json_str: str) -> None:
        try:
            pipe = self._redis.pipeline()
            pipe.rpush(self._keys.backlog, json_str)
            pipe.ltrim(
                name=self._keys.backlog,
                start=-self._max_len,
                end=-1
            )
            pipe.publish(
                channel=self._keys.channel,
                message=json_str
            )
            await pipe.execute()
        except aioredis.RedisError as e:
            logger.error(f'Failed to push log entry to Redis: {e}', exc_info=e)
            await asyncio.sleep(0.5)
