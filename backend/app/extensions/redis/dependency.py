from types import CoroutineType
from typing import Annotated, Any, Callable

from fastapi import Depends
from .client import RedisClient, RedisConnection
import redis.asyncio as aioredis

async def redis_client() -> aioredis.Redis: # type: ignore 
    '''creates a dependency to get the redis client'''
    async with RedisConnection.client() as client:
        yield client # type: ignore

async def get_redis_client() -> RedisClient:
    '''creates a dependency to get the redis client'''
    return RedisClient()

def redis_client_maker(key_prefix: str):
    async def create_client_dep() -> RedisClient:
        '''creates a dependency to get the redis client'''
        return RedisClient(key_prefix)    
    return create_client_dep


# This is "unsafe" because it doesn't sanitize inputs before passed and is the unwrapped redis client
UnsafeRedisDep = Annotated[aioredis.Redis, Depends(redis_client)]
RedisClientDep = Annotated[RedisClient, Depends(get_redis_client)]