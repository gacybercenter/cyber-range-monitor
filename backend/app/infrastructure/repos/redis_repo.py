import abc
from enum import StrEnum
from redis import asyncio as aioredis
from redis.asyncio import client as aioredis_client
from collections import defaultdict

from typing import Any, Callable, Generic, TypeVar


C = TypeVar('C', bound=StrEnum)


class RedisCommandAdapter(Generic[C]):
    def __init__(self) -> None:
        self.__commands: dict[C, Callable[..., Any]] = {}

    def run(
        self, command: C, pipepline: aioredis_client.Pipeline, **kwargs: Any
    ) -> Any:
        command_fn = self.__commands.get(command)
        if command_fn is None:
            raise RuntimeError(f'Command {command} not registered')

        return command_fn(**kwargs)


class RedisRepository:
    def __init__(self, redis_client: aioredis.Redis) -> None:
        self.redis_client: aioredis.Redis = redis_client
