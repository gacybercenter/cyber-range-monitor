from typing import Annotated

from fastapi import Depends
from .client import RedisClient


async def get_redis_client() -> RedisClient:
    '''async dependency function to get the redis client'''
    return RedisClient.get_instance()


RedisDep = Annotated[RedisClient, Depends(get_redis_client)]