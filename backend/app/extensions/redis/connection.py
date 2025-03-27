from typing import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis

from app import config

from .errors import (
    RedisClientError,
    RedisConnectionError,
    RedisNotConnectedError
)
from .const import (
    SOCKET_CONNECT_TIMEOUT,
    SOCKET_TIMEOUT,
    MAX_CONNECTIONS
)


class RedisConnection:
    '''Redis conn for the application as a singleton class wrapper
    to manage the conn instance and sanitize key inputs 
    Raises:
        ConnectionError: if the connections fails or an action is performed
        before the connection is established
    '''
    _instance: 'RedisConnection' = None  # type: ignore
    _conn: 'aioredis.Redis' = None  # type: ignore

    @classmethod
    def _create_conn(cls) -> aioredis.Redis:
        '''creates the redis conn 

        Arguments:
            options {RedisOptions} -- the options for the redis conn

        Returns:
            aioredis.Redis -- the conn instance
        '''
        config_yml = config.get_config_yml()
        environment = config_yml.app.environment
        password = None
        if environment != "local":
            password = config.get_secrets().redis_password
        redis_url = config_yml.redis.get_url(password)
        return aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=SOCKET_CONNECT_TIMEOUT,
            socket_timeout=SOCKET_TIMEOUT,
            max_connections=MAX_CONNECTIONS
        )

    @classmethod
    async def connect(cls) -> bool:
        '''opens the connection with the redis conn 

        Arguments:
            options {dict} -- the serialized "RedisOptions"

        Raises:
            ConnectionError: if the connection fails or has already been established

        Returns:
            bool -- whether or not the connection was sucessfully established
        '''
        if cls._instance and cls._conn:
            return True
        cls._instance = cls()
        cls._conn = cls._create_conn()
        try:
            result = await cls._conn.ping()
            return bool(result)
        except Exception as e:
            raise ConnectionError(
                f'RedisConnectionError: Failed to connect to Redis.\nDetails:\n\t{e}\n\n') from e

    @classmethod
    async def disconnect(cls) -> None:
        '''closes the connection to the redis server'''
        if not cls._instance or not cls._conn:
            return
        await cls._conn.close()

    @classmethod
    def get_conn(cls) -> 'RedisConnection':
        if not cls._instance or not cls._conn:
            raise RedisNotConnectedError()
        return cls._instance

    @classmethod
    @asynccontextmanager
    async def client(cls) -> AsyncGenerator[aioredis.Redis, None]:
        '''creates a dependency to get the redis conn connection
        Returns:
            RedisConnection -- the redis conn connection
        '''
        if not await cls.is_alive() and not await cls.connect():
            raise RedisConnectionError(
                'Redis is not connected. Call connect() first.'
            )
        try:
            yield cls._conn
        except Exception as e:
            raise RedisClientError(
                f"An error occured while using the redis conn.\nDetails:\n\t{e}\n\n"
            ) from e

    @classmethod
    async def is_alive(cls, test_conn: bool = False) -> bool:
        '''checks if the redis conn is connected and optionally pings the server

        Keyword Arguments:
            test_conn {bool} -- whether or not to test the connection (default: {False})

        Returns:
            bool -- whether or not the redis conn is connected
        '''
        conn_established = not cls._instance or not cls._conn
        if not test_conn or not conn_established:
            return conn_established
        ping_result = await cls._conn.ping()
        return bool(ping_result)
