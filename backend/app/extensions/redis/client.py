from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional
import re

from .connection import RedisConnection

import redis.asyncio as aioredis


def sanitize_key(key: str) -> str:
    """sanitizes redis keys before passed to the client to prevent 
    injection attacks.

    Arguments:
        key {str} -- the key to sanitize

    Returns:
        str -- the sanitized key
    """
    sanitized_key = re.sub(r'[^a-zA-Z0-9_\-:]', '', key)

    if sanitized_key.lower().startswith(('eval', 'exec', 'flushall', 'flushdb', 'keys')):
        sanitized_key = f"safe_{sanitized_key}"

    return sanitized_key


class RedisClient:
    '''A class to interact with the Redis client connection with all of the 
    safety checks in place to ensure the client is connected and the keys are sanitized
    '''

    def __init__(self, key_prefix: Optional[str] = None) -> None:
        '''initializes the redis client with a key prefix

        Arguments:
            key_prefix {Optional[str]} -- the prefix to prepend to all keys
        '''
        self.key_prefix: Optional[str] = key_prefix

    def sanitize(self, key: str) -> str:
        '''sanitizes and prepends the key prefix to the key (if set)
        Arguments:
            key {str} -- the key to sanitize and prepend the prefix to
        Returns:
            str -- the sanitized and prefixed key
        '''
        sanitized = sanitize_key(key)
        if not self.key_prefix:
            return sanitized
        return f'{self.key_prefix}:{sanitized}'

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        '''sets a value in the redis store by key

        Arguments:
            key {str} -- the key to set the value for
            value {Any} -- the value to set for the key

        Keyword Arguments:
            ex {int | None} -- the expiration in seconds for the key
        '''
        key = self.sanitize(key)
        async with RedisConnection.client() as client:
            await client.set(key, value, ex=ex)

    async def get(self, key: str) -> Optional[str]:
        '''gets a value from the redis store by key

        Arguments:
            key {str} -- the key to get the value for

        Returns:
            Any -- the value for the key
        '''
        key = self.sanitize(key)
        async with RedisConnection.client() as client:
            return await client.get(key)

    async def expire(self, key: str, ex: int) -> None:
        '''sets the expiration time for a key in the redis store
        Arguments:
            key {str} -- the key to set the expiration time for
            ex {int} -- the expiration time in seconds
        '''
        key = self.sanitize(key)
        async with RedisConnection.client() as client:
            await client.expire(key, ex)

    async def delete(self, key: str) -> None:
        '''deletes a key from the redis store

        Arguments:
            key {str} -- the key to delete
        '''
        key = self.sanitize(key)
        async with RedisConnection.client() as client:
            await client.delete(key)

    async def get_conn(self) -> aioredis.Redis:
        '''returns a connection to the redis client NOTE
        ENSURE YOU SANITIZE ALL INPUTS BEFORE HAND

        Returns:
            aioredis.Redis
        '''
        async with RedisConnection.client() as client:
            return client

    async def hset(self, key: str, mapping: dict) -> None:
        '''sets a hash in the redis store by key

        Arguments:
            key {str} -- the key to set the hash for
            mapping {dict} -- the hash to set for the key
        '''
        key = self.sanitize(key)
        async with RedisConnection.client() as client:
            client.hset(key, mapping=mapping)

    # async def hgetall(self, key: str) -> dict:
    #     '''gets a hash from the redis store by key

    #     Arguments:
    #         key {str} -- the key to get the hash for

    #     Returns:
    #         dict -- the hash for the key
    #     '''
    #     key = self.sanitize(key)
    #     async with RedisConnection.client() as client:
    #         return await client.hgetall(key)
