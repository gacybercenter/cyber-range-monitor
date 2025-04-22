from typing import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis

from app import config
import logging

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

redis_logger = logging.getLogger("redis")


class RedisConnection:
    '''Redis conn for the application as a singleton class wrapper
    to manage the conn instance and sanitize key inputs 
    Raises:
        ConnectionError: if the connections fails or an action is performed
        before the connection is established
    Attributes:
        _instance {RedisConnection} -- the single instance of the class
        _conn {aioredis.Redis} -- the created and single instance of the redis 
        client
        _url {str} -- the computed redis url to connect to using the api config  
    '''
    _instance: 'RedisConnection' = None  # type: ignore
    _conn: 'aioredis.Redis' = None  # type: ignore
    _url: str = None  # type: ignore

    @classmethod
    def get_url(cls) -> str:
        '''gets the proper redis url based on the app environment

        Returns:
            str -- the redis URL
        '''
        if cls._url:
            return cls._url
        config_yml = config.get_config_yml()
        environment = config_yml.app.environment
        password = None
        if environment != "local":
            password = config.get_secrets().redis_password
        cls._url = config_yml.redis.get_url(password)
        redis_logger.info(
            f'[italic]Resolved Redis URL to:[/italic] [bold blue]{cls._url}[/bold blue]',
        )
        return cls._url

    @classmethod
    def _create_conn(cls) -> aioredis.Redis:
        '''creates the redis conn 

        Arguments:
            options {RedisOptions} -- the options for the redis conn

        Returns:
            aioredis.Redis -- the redis instance
        '''
        global redis_logger
        redis_logger.info(
            '[italic] Attempting to establish a connection with [/italic] '
            '[bold blue] Redis...[/bold blue]'
        )

        return aioredis.from_url(
            cls.get_url(),
            decode_responses=True,
            socket_connect_timeout=SOCKET_CONNECT_TIMEOUT,
            socket_timeout=SOCKET_TIMEOUT,
            max_connections=MAX_CONNECTIONS
        )

    @classmethod
    async def connect(cls) -> bool:
        '''opens the connection with the redis connection and creates the class
        instance

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
            redis_logger.critical(
                '[red] Failed to connect to Redis[/red] '
                '[bold blue] likely due to a misconfiguration check the config.yml file.'
                '[/bold blue]',
                exc_info=e
            )

            raise ConnectionError(
                f'RedisConnectionError: Failed to connect to Redis.\nDetails:\n\t{e}\n\n'
            ) from e

    @classmethod
    async def disconnect(cls) -> None:
        '''closes the connection to the redis server'''
        if not cls._instance or not cls._conn:
            return
        redis_logger.info(
            '[italic blue] Disconnecting Redis connection...[/italic blue]')
        await cls._conn.close()

    @classmethod
    def get_conn(cls) -> 'RedisConnection':
        '''gets the connection instance, not reccomended

        Raises:
            RedisNotConnectedError: if the connection has not been established

        Returns:
            RedisConnection -- the redis connection instance
        '''
        if not cls._instance or not cls._conn:
            raise RedisNotConnectedError()
        return cls._instance

    @classmethod
    @asynccontextmanager
    async def client(cls) -> AsyncGenerator[aioredis.Redis, None]:
        '''context manager which wraps the redis client instance in a try 
        block to handle connection errors and ensure the connection is alive
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
            global redis_logger
            redis_logger.error(
                '[red] An unhandled error occured while using '
                ' the[/red] [bold blue]asyncio.Redis [/bold blue] '
                '[red]instance[/red] ',
                exc_info=e
            )
            raise RedisClientError(
                f"An error occured while using the asyncio.Redis instance.\nDetails:\n\t{e}\n\n"
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
        msg = '[bold green]alive[/bold green]' if ping_result else '[bold red]unavailable[/bold red]'
        redis_logger.info(
            f'[italic blue] Pinged Redis and Redis is [/italic blue] {msg}')
        return bool(ping_result)
