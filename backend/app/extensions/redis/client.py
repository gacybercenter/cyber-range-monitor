from typing import Any
import redis.asyncio as aioredis

from .options import RedisOptions
from app import config
import re


def create_client(options: RedisOptions) -> aioredis.Redis:
    '''creates the redis client 

    Arguments:
        options {RedisOptions} -- the options for the redis client

    Returns:
        aioredis.Redis -- the client instance
    '''
    config_yml = config.get_config_yml()
    environment = config_yml.app.environment
    password = None
    if environment != "local":
        password = config.get_secrets().redis_password
    redis_url = config_yml.redis.get_url(password)
    init_args = options.model_dump()
    return aioredis.from_url(
        redis_url,
        decode_responses=True,
        **init_args
    )


def sanitize(key: str) -> str:
    """Sanitize a Redis key to prevent injection attacks.

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
    '''Redis client for the application as a singleton
    Raises:
        ConnectionError: if the connections fails or an action is performed
        before the connection is established
    '''
    _instance: 'RedisClient' = None  # type: ignore
    _client: 'aioredis.Redis' = None  # type: ignore

    @classmethod
    async def connect(cls, options: RedisOptions = RedisOptions()) -> bool:
        if cls._instance:
            raise ConnectionError(
                "RedisClient instance already exists. Use get_instance() to access it.")
        cls._instance = cls()
        cls._client = create_client(options)
        result = await cls._client.ping()
        return bool(result)

    def _ensure_connected(self) -> None:
        if not self._instance or not self._client:
            raise ConnectionError(
                "RedisClient was never not connected and is unavailable. Call connect() first."
            )

    @classmethod
    def get_instance(cls) -> 'RedisClient':
        if cls._instance is None:
            raise ConnectionError(
                "RedisClient was never not connected and is unavailable. Call connect() first."
            )
        return cls._instance

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        '''sets a value in the redis store by key

        Arguments:
            key {str} -- the key to set the value for
            value {Any} -- the value to set for the key

        Keyword Arguments:
            ex {int | None} -- the expiration in seconds for the key
        '''
        self._ensure_connected()
        key = sanitize(key)
        await self._client.set(key, value, ex=ex)

    async def get(self, key: str) -> Any:
        '''gets a value from the redis store by key

        Arguments:
            key {str} -- the key to get the value for

        Returns:
            Any -- the value for the key
        '''
        self._ensure_connected()
        key = sanitize(key)
        return await self._client.get(key)

    async def expire(self, key: str, ex: int) -> None:
        '''sets the expiration time for a key in the redis store
        Arguments:
            key {str} -- the key to set the expiration time for
            ex {int} -- the expiration time in seconds
        '''
        self._ensure_connected()
        key = sanitize(key)
        await self._client.expire(key, ex)

    async def delete(self, key: str) -> None:
        '''deletes a key from the redis store

        Arguments:
            key {str} -- the key to delete
        '''
        self._ensure_connected()
        key = sanitize(key)
        await self._client.delete(key)

    @classmethod
    async def close_conn(cls) -> None:
        '''closes the connection to the redis server'''
        if not cls._instance or not cls._client:
            return
        await cls._client.close()