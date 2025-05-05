
import asyncio
from contextlib import asynccontextmanager
import json

import uuid

from datetime import datetime
from typing import AsyncGenerator, Dict, List

import redis.asyncio as aioredis

from fastapi import WebSocket, WebSocketDisconnect, status


from .schema import LogEntry, LogFilter, WebsocketResponse, WebsocketCommand
from . import websocket_handler
from .const import (
    LOG_BUFFER_SIZE,
    LOG_CHANNEL,
    MAX_CONNECTIONS,
    MAX_MSG_SIZE,
    PING_INTERVAL,
    PING_TIMEOUT
)


class LogSocketConnection:
    def __init__(
        self,
        *,
        websocket: WebSocket,
        filter: LogFilter | None = None
    ) -> None:
        self.connection_id: str = str(uuid.uuid4())
        self.filter = filter
        self.socket = websocket
        self.last_active: datetime = datetime.now()
        self.idle = False

    def update_last_active(self) -> None:
        self.last_active = datetime.now()

    def update_filter(
        self,
        filter: LogFilter | None = None
    ) -> None:
        self.filter = filter
        self.update_last_active()

    def pause(self) -> None:
        self.idle = True
        self.update_last_active()

    def resume(self) -> None:
        self.idle = False
        self.update_last_active()

    async def send_log(
        self,
        entry: LogEntry
    ) -> bool:
        if self.idle:
            return True

        if self.filter and self.filter.matches(entry):
            return True

        result = False
        try:
            response = WebsocketResponse.as_log(
                entry=entry
            )
            await self.socket.send_json(response)
            result = True
        except Exception:
            pass

        return result

    async def send_error(
        self,
        error: str
    ) -> bool:
        result = False
        try:
            response = WebsocketResponse.as_error(
                message=error
            )
            await self.socket.send_json(response)
            result = True
        except Exception:
            pass

        return result

    async def send_notice(self, message: str) -> bool:
        result = False
        try:
            response = WebsocketResponse.as_notice(
                message=message
            )
            await self.socket.send_json(response)
            result = True
        except Exception:
            pass
        return result

    async def ping(self) -> bool:
        result = False
        try:
            response = WebsocketResponse.as_ping()
            await self.socket.send_json(response)
            result = True
        except Exception:
            pass
        return result


class _SocketIter:
    __slots__ = ('should_disconnect', 'connection')

    def __init__(self, connection: LogSocketConnection) -> None:
        self.connection = connection
        self.should_disconnect = False


class LogSocketManager:
    def __init__(self) -> None:
        self.connections: Dict[str, LogSocketConnection] = {}
        self.ping_task: asyncio.Task | None = None
        self.ping_interval = PING_INTERVAL

    async def socket_iter(self) -> AsyncGenerator[_SocketIter, None]:
        '''Iterates over the active connections and yields a context for each connection.
        the context is used to check if the connection should be disconnected allowing 
        for an action to be performed and then using the result of the action to determine if the 
        connection should be closed.

        Yields:
            _SocketIter: A context for the connection (should_disconnect is set to True if the connection should be closed).

        '''
        to_disconnect = set()
        for conn_id, connection in self.connections.items():
            next_conn = _SocketIter(
                connection=connection
            )
            
            yield next_conn
            
            if next_conn.should_disconnect:
                to_disconnect.add(conn_id)

        for conn_id in to_disconnect:
            await self.disconnect(conn_id)

    async def _begin_ping_task(self) -> None:
        if self.ping_task:
            return
        self.ping_task = asyncio.create_task(self._ping_connections())

    async def connect(
        self,
        socket: WebSocket,
        filter: LogFilter | None = None
    ) -> LogSocketConnection:
        try:
            await socket.accept()
            connection = LogSocketConnection(
                websocket=socket,
                filter=filter
            )
            conn_id = connection.connection_id
            self.connections[conn_id] = connection
            if len(self.connections) == 1 and not self.ping_task:
                await self._begin_ping_task()
            return connection
        except Exception as e:
            raise

    async def disconnect(self, conn_id: str) -> None:
        if not conn_id in self.connections:
            return
        try:
            self.connections.pop(conn_id)
            if not self.connections and self.ping_task:
                self.ping_task.cancel()
                self.ping_task = None
        except Exception as e:
            raise

    async def broadcast(self, log: LogEntry) -> None:
        async for context in self.socket_iter():
            context.should_disconnect = await context.connection.send_log(log)

    async def _ping_connections(self) -> None:
        try:
            while True:
                await asyncio.sleep(self.ping_interval)
                async for context in self.socket_iter():
                    connection = context.connection
                    context.should_disconnect = await connection.ping()
        except asyncio.CancelledError:
            pass

    async def close_all(self) -> None:
        '''Closes all connections and cancels the ping task.'''
        for connections in list(self.connections.values()):
            try:
                await connections.socket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason="Server shutdown"
                )
            except Exception:
                pass

        self.connections.clear()
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None


class AsyncLoggerTaskManager:

    def __init__(
        self,
        queue: asyncio.Queue[LogEntry],
        loggers: List[str],
        redis: aioredis.Redis,
    ) -> None:
        self.queue = queue
        self.loggers = loggers
        self.redis = redis
        self._pubsub_task: asyncio.Task | None = None
        self._queue_task: asyncio.Task | None = None
        self._is_running = False

        self._log_buffer: List[LogEntry] = []

    async def start(self, socket_manager: LogSocketManager) -> None:
        if self._is_running:
            return
        websocket_handler.setup_async_queue_handler(
            queue=self.queue,
            logger_names=self.loggers
        )

        self._pubsub_task = asyncio.create_task(
            self._pubsub_listener(socket_manager)
        )
        self._queue_task = asyncio.create_task(
            self._queue_waiter(socket_manager)
        )
        self._is_running = True

    async def end(self) -> None:
        if not self._is_running:
            return

        if self._pubsub_task:
            self._pubsub_task.cancel()
            self._pubsub_task = None

        if self._queue_task:
            self._queue_task.cancel()
            self._queue_task = None

        websocket_handler.remove_async_queue_handler(
            logger_names=self.loggers
        )

    async def _pubsub_listener(self, socket_manager: LogSocketManager) -> None:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(LOG_CHANNEL)
        try:
            async for message in pubsub.listen():
                if message['type'] != 'message':
                    continue
                data = json.loads(message['data'])
                log_entry = LogEntry(**data)
                await self._append_to_buffer(data=log_entry)
                await socket_manager.broadcast(log_entry)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(LOG_CHANNEL)
            await pubsub.close()
            raise
        except Exception as e:
            await pubsub.unsubscribe(LOG_CHANNEL)
            await pubsub.close()

    async def _append_to_buffer(self, data: LogEntry) -> None:
        self._log_buffer.append(data)
        if len(self._log_buffer) >= LOG_BUFFER_SIZE:
            self._log_buffer = self._log_buffer[-LOG_BUFFER_SIZE:]

    async def _queue_waiter(self, socket_manager: LogSocketManager) -> None:
        '''Handles the queue task and processes the log entries from the queue.'''
        try:
            while True:
                new_entry = await self.queue.get()
                await self._append_to_buffer(
                    new_entry
                )

                try:
                    await self.redis.publish(
                        LOG_CHANNEL,
                        new_entry.model_dump_json(exclude_none=True)
                    )
                except Exception:
                    pass
                await socket_manager.broadcast(new_entry)
                self.queue.task_done()
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    async def get_recent_logs(
        self,
        filter: LogFilter | None = None
    ) -> List[LogEntry]:
        '''Returns the recent logs from the log buffer.

        Args:
            filter (LogFilter | None, optional): _the filter to use_. Defaults to None.

        Returns:
            List[LogEntry]: _the recent logs_
        '''
        if not filter:
            return self._log_buffer.copy()
        return [
            entry for entry in self._log_buffer
            if filter.matches(entry)
        ]


class RealtimeLogService:

    def __init__(
        self,
        *,
        redis_client: aioredis.Redis,
        loggers: List[str]
    ) -> None:
        self.redis = redis_client
        self.loggers = loggers
        self.log_queue: asyncio.Queue[LogEntry] = asyncio.Queue(
            maxsize=LOG_BUFFER_SIZE
        )
        self.pubsub_task: asyncio.Task | None = None
        self.queue_task: asyncio.Task | None = None
        self.socket_manager = LogSocketManager()
        self.task_manager = AsyncLoggerTaskManager(
            queue=self.log_queue,
            loggers=self.loggers,
            redis=self.redis
        )

    async def start_tasks(self) -> None:
        '''Starts the tasks for the log service.'''
        await self.task_manager.start(
            socket_manager=self.socket_manager
        )

    async def end_tasks(self) -> None:
        '''Ends the tasks for the log service.'''
        await self.task_manager.end()
        await self.socket_manager.close_all()

    async def _try_send_recent_logs(
        self,
        connection: LogSocketConnection
    ) -> None:
        recent_logs = await self.task_manager.get_recent_logs(
            filter=connection.filter
        )
        for log in recent_logs:
            success = await connection.send_log(log)
            if not success:
                await self.socket_manager.disconnect(
                    conn_id=connection.connection_id
                )

    @asynccontextmanager
    async def _websocket_context(
        self,
        web_socket: WebSocket,
        filter: LogFilter | None
    ):
        '''wraps the websocket connection in a context manager to 
        handle the connection lifecycle and to provide exception handling
        without insane code indentation and manages the initial connection
        setup.

        Args:
            web_socket (WebSocket): _description_
            filter (LogFilter | None): _description_

        Yields:
            _type_: _description_
        '''
        try:
            connection = await self.socket_manager.connect(
                socket=web_socket,
                filter=filter
            )
            await connection.send_notice(
                message="Connected to log stream."
            )
            await self._try_send_recent_logs(connection)

            yield connection

        except WebSocketDisconnect:
            pass
        except Exception as e:
            await self._try_close_socket(web_socket)
        finally:
            if 'connection' in locals():
                await self.socket_manager.disconnect(
                    conn_id=connection.connection_id  # type: ignore
                )

    async def manage_websocket(
        self,
        web_socket: WebSocket,
        filter: LogFilter | None = None
    ) -> None:
        '''Handles the websocket connection and processes the incoming messages and is wrapped
        in a context manager to handle the connection lifecycle and to provide exception handling

        Args:
            web_socket (WebSocket): _the client websocket_
            filter (LogFilter | None, optional): _the filter for the websocket_. Defaults to None.
        '''
        async with self._websocket_context(web_socket, filter) as conn:
            while True:
                try:
                    json_str = await asyncio.wait_for(
                        conn.socket.receive_text(),
                        timeout=60
                    )
                    await self._proccess_command(conn, json_str)
                except asyncio.TimeoutError:
                    procceed = await conn.ping()
                    if not procceed:
                        break
                except WebSocketDisconnect:
                    break

    async def _try_close_socket(self, web_socket: WebSocket,) -> None:
        '''Handles the closing of the websocket connection and sends a 
        closing frame to the client.

        Args:
            web_socket (WebSocket): _the websocke to close_
        '''
        try:
            await web_socket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Server error"
            )
        except Exception:
            pass

    async def _proccess_command(self, connection: LogSocketConnection, json_str: str) -> None:
        '''Processes the command received from the websocket and updates the connection state accordingly.'''
        if len(json_str) > MAX_MSG_SIZE:
            await connection.send_error(
                error=f"Message too long ({len(json_str)} > {MAX_MSG_SIZE})"
            )
            return

        try:
            cmd_schema = WebsocketCommand.model_validate_json(json_str)
        except Exception:
            await connection.send_error(
                error="Invalid or unknown command format"
            )
            return

        connection.update_last_active()
        if cmd_schema.is_filter():
            connection.update_filter(
                filter=cmd_schema.filter
            )
            await connection.send_notice(message="Filter updated")
        elif cmd_schema.is_pause():
            connection.pause()
            await connection.send_notice(message="Log stream paused.")
        elif cmd_schema.is_resume():
            connection.resume()
            await connection.send_notice(message="Log stream resumed.")
        else:
            await connection.send_error(
                error="Invalid or unknown command format"
            )
