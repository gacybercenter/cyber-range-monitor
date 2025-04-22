from typing import Any, Optional

import redis.asyncio as aioredis

from .connection import RedisConnection

from .keys import RedisKey


class RedisClient:
    '''A Wrapper to interact with the Redis client connection with all of the 
    safety checks in place to ensure the client is connected and keys are sanitized
    before use and allowing easy dependency injection for dependant routes 
    '''

    def __init__(self, key_prefix: str | None = None) -> None:
        self.key_prefix: Optional[str] = key_prefix

    def create_key(self, orig_key: str) -> RedisKey:
        '''creates a redis key from the original key and the prefix.
        Arguments:
            orig_key {str} -- the original key to create the redis key from
        Raises:
            InvalidRedisKey -- if the key is invalid
        Returns:
            RedisKey -- the safe redis key
        '''
        return RedisKey(orig_key, self.key_prefix)

    async def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None
    ) -> bool:
        '''sets a value in the redis store by key

        Arguments:
            key {str} -- the key to set the value for
            value {Any} -- the value to set for the key

        Keyword Arguments:
            ex {int | None} -- the expiration in seconds for the key
        '''
        safe_key = RedisKey(key, self.key_prefix)
        async with RedisConnection.client() as client:
            await client.set(
                safe_key,
                value,
                ex=ex
            )
        return True

    async def get(self, key: str) -> Optional[str]:
        '''gets a value from the redis store by key

        Arguments:
            key {str} -- the key to get the value for

        Returns:
            Any -- the value for the key
        '''
        safe_key = RedisKey(key, self.key_prefix)
        async with RedisConnection.client() as client:
            return await client.get(safe_key)

    async def expire(self, key: str, ex: int) -> None:
        '''sets the expiration time for a key in the redis store
        Arguments:
            key {str} -- the key to set the expiration time for
            ex {int} -- the expiration time in seconds
        '''
        safe_key = RedisKey(key, self.key_prefix)
        async with RedisConnection.client() as client:
            await client.expire(safe_key, ex)

    async def delete(self, key: str) -> None:
        '''deletes a key from the redis store

        Arguments:
            key {str} -- the key to delete
        '''
        safe_key = RedisKey(key, self.key_prefix)
        async with RedisConnection.client() as client:
            await client.delete(safe_key)

    async def exists(self, key: str) -> bool:
        '''checks if a key exists in the redis store

        Arguments:
            key {str} -- the key to check 

        Returns:
            bool -- the result
        '''
        safe_key = RedisKey(key, self.key_prefix)
        async with RedisConnection.client() as client:
            return await client.exists(safe_key)

    async def get_conn(self) -> aioredis.Redis:
        '''returns a connection to the redis client NOTE
        ENSURE YOU SANITIZE ALL INPUTS BEFORE HAND

        Returns:
            aioredis.Redis
        '''
        async with RedisConnection.client() as client:
            return client
