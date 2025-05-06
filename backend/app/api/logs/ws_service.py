import asyncio
import logging

import queue
from typing import AsyncGenerator
from fastapi import WebSocket, WebSocketDisconnect, status
import redis.asyncio as aioredis

from .schema import (
    CommandResponse,
    LogEntry,
    WebSocketCommand,
    LogFilter
)
from .log_consumer import RedisLogConsumer


def filter_allows(
    client: 'ClientWebsocket',
    entry: LogEntry
) -> bool:
    '''Checks if the log entry matches the filter of the client.

    Args:
        client (ClientWebsocket): _the client_
        entry (LogEntry): _the entry to check__

    Returns:
        bool: _whether the filter allows the log entry_
    '''
    no_filter = client.filter is None
    meets_filter = client.filter is not None and client.filter.matches(entry)
    return no_filter or meets_filter


class ClientStreams:
    '''Represents the dedicated stream for a connected client on the 
    logger websocket 
    '''

    def __init__(
        self,
        *,
        client_id: str,
        redis: aioredis.Redis,
        queue: queue.Queue,
        max_len: int,
        max_connection: int,
        filter: LogFilter | None,
    ) -> None:
        self.client_id: str = client_id

        self._consumer: RedisLogConsumer = RedisLogConsumer(
            std_queue=queue,
            redis=redis,
            client_id=client_id,
        )
        self.max_len: int = max_len
        self.max_connections: int = max_connection
        self._lock = asyncio.Lock()
        self.filter: LogFilter | None = filter
        self._conns: set['ClientWebsocket'] = set()

        self._pubsub_task: asyncio.Task | None = None

    async def _pubsub_loop(self) -> None:
        '''subscribes to the redis channel and sends log entries 
        to all connected clients.
        '''
        async for message in self._consumer.listener():
            if not message or message.get('type') != 'message':
                continue
            data = message.get('data')
            if not data:
                continue
            entry = LogEntry.model_validate_json(data)
            todos = []
            for conn in self._conns:
                if conn.paused or filter_allows(conn, entry):
                    continue
                todos.append(
                    conn.web_socket.send_json(
                        entry.serialize()
                    )
                )
            if todos:
                await asyncio.gather(*todos, return_exceptions=True)

    def _begin(self) -> None:
        '''begins the consumer and the pubsub task if it is not already running.'''
        self._consumer.start()
        self._pubsub_task = asyncio.create_task(
            self._pubsub_loop()
        )

    def _stop(self) -> None:
        '''stops the consumer and the pubsub task if it is running.'''
        self._consumer.stop()
        if self._pubsub_task:
            self._pubsub_task.cancel()
            self._pubsub_task = None

    async def connect(self, client: 'ClientWebsocket') -> None:
        '''connects a new client to the stream and starts the consumer if it is not already running.

        Args:
            client (ClientWebsocket): _the client to connect_

        Raises:
            WebSocketDisconnect: _when the client disconnects_
        '''
        async with self._lock:

            self._conns.add(client)
            if len(self._conns) == 1:
                self._begin()

    async def disconnect(self, client: 'ClientWebsocket') -> None:
        '''disconnects a client from the stream and stops the consumer if there 
        are no more clients.

        Args:
            client (ClientWebsocket): _the client to disconnect_
        '''
        async with self._lock:
            self._conns.discard(client)
            if not self._conns:
                self._stop()

    async def iter_backlog(self) -> AsyncGenerator[LogEntry, None]:
        '''iterates of the backlog of the stream and yields log entries.

        Returns:
            AsyncGenerator[LogEntry, None]: _the log entries_

        Yields:
            Iterator[AsyncGenerator[LogEntry, None]]: _the log entries_
        '''
        backlog = await self._consumer.get_backlog()
        for raw_json in backlog:
            try:
                entry = LogEntry.model_validate_json(raw_json)
            except Exception:
                continue
            yield entry


class ClientWebsocket:
    def __init__(self, web_socket: WebSocket, stream: ClientStreams) -> None:
        self.web_socket: WebSocket = web_socket
        self.streams: ClientStreams = stream
        self.paused: bool = False
        self.filter: LogFilter | None = None
        self._cmd_task: asyncio.Task | None = None

    async def run(self) -> None:
        '''runs the websocket handler and starts the command loop.'''
        await self.streams.connect(self)
        try:
            await self.send_backlog()
            self._cmd_task = asyncio.create_task(self._command_loop())
            await self._cmd_task
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logging.exception(
                "An error occurred in the websocket handler", exc_info=e)
            await self.web_socket.close(code=status.WS_1011_INTERNAL_ERROR)
        finally:
            await self.streams.disconnect(self)
            await self.web_socket.close()
            if self._cmd_task:
                self._cmd_task.cancel()
                self._cmd_task = None

    async def send_backlog(self) -> None:
        '''sends the backlog of logs to the client.'''
        async for entry in self.streams.iter_backlog():
            if filter_allows(self, entry):
                await self.web_socket.send_json(
                    entry.serialize()
                )

    async def _command_loop(self) -> None:
        '''task handling commands from the client and sends responses.'''
        while True:
            data = await self.web_socket.receive_json()

            try:
                command = WebSocketCommand.model_validate(data)
            except Exception:
                await self.web_socket.send_json(
                    data=CommandResponse.fail('invalid-command')
                )
                continue

            res = CommandResponse.fail('unknown-command')
            if command.is_pause():
                res = (
                    CommandResponse.fail('already-paused') if self.paused
                    else CommandResponse.ok('pasued')
                )
                self.paused = True
                await self.web_socket.send_json(res)
            elif command.is_resume():
                res = (
                    CommandResponse.fail('already-resumed') if not self.paused
                    else CommandResponse.ok('resumed')
                )
                await self.web_socket.send_json(res)
            elif command.is_filter():
                self.filter = command.filter
                res = CommandResponse.ok('filter-set')
                await self.send_backlog()
                await self.web_socket.send_json(res)
            else:
                await self.web_socket.send_json(res)


class LogSocketManager:
    def __init__(
        self,
        *,
        redis: aioredis.Redis,
        q: queue.Queue,
        max_len: int = 1000,
        max_connections: int = 10
    ) -> None:
        self.redis: aioredis.Redis = redis
        self.queue: queue.Queue = q
        self._streams: dict[str, ClientStreams] = {}
        self.max_len: int = max_len
        self.max_connections: int = max_connections

        self._lock = asyncio.Lock()

    async def handle(
        self,
        *,
        web_socket: WebSocket,
        client_id: str,
        initial_filter: LogFilter | None
    ) -> None:
        async with self._lock:
            stream = self._streams.get(client_id)
            if not stream:
                stream = ClientStreams(
                    client_id=client_id,
                    redis=self.redis,
                    queue=self.queue,
                    max_len=self.max_len,
                    max_connection=self.max_connections,
                    filter=initial_filter,
                )
                self._streams[client_id] = stream

            await web_socket.accept()
            client = ClientWebsocket(
                web_socket=web_socket,
                stream=stream
            )
            await client.run()
