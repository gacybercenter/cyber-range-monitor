import json
import asyncio
import weakref

import redis.asyncio as aioredis

from typing import Any, Callable, Awaitable
from loguru import logger

from .schema import LogEntry


class AsyncTask:
    def __init__(
        self, async_fn: Callable[..., Awaitable[Any]], context: dict | None = None
    ) -> None:
        self.async_fn = async_fn
        self.context = context or {}
        self._running = False
        self._task: asyncio.Task | None = None

    async def begin(self) -> None:
        """Start the async task"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._exec_wrapper())

    async def end(self) -> None:
        """Stop the async task"""
        if not self._running:
            return
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self._running = False

    async def _exec_wrapper(self) -> None:
        """Wrapper to execute the async function"""
        try:
            await self.async_fn(**self.context)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception(f"Error in async task: {e}")
        finally:
            self._running = False


class LogBacklog:
    """Centralized queue manager for thread-safe log processing"""

    def __init__(self, max_queue_size: int = 10000) -> None:
        self.log_queue = asyncio.Queue(maxsize=max_queue_size)
        self._subscribers: set[weakref.ref] = set()
        self._process_task: AsyncTask = AsyncTask(async_fn=self._process_queue)
        self._running = False

    async def start(self) -> None:
        """Start the queue processing"""
        if self._running:
            return

        self._running = True
        await self._process_task.begin()
        logger.info("Queue manager started")

    async def stop(self) -> None:
        """Stop the queue processing and clean up"""
        if not self._running:
            return

        self._running = False
        await self._process_task.end()
        logger.info("Queue manager stopped")

    async def enqueue(self, log_entry: LogEntry) -> bool:
        """Add a log entry to the queue, return True if successful"""
        if not self._running:
            return False

        try:
            if self.log_queue.full():
                return False
            await self.log_queue.put(log_entry)
            return True
        except Exception as e:
            return False

    def subscribe(self, callback: Callable[[LogEntry], Awaitable[None]]) -> None:
        self._subscribers.add(weakref.ref(callback, self._finalizer))

    def unsubscribe(self, callback: Callable[[LogEntry], Awaitable[None]]) -> None:
        to_remove = None
        for ref in self._subscribers:
            if ref() == callback:
                to_remove = ref
                break

        if to_remove:
            self._subscribers.remove(to_remove)

    def _finalizer(self, ref) -> None:
        """Called when a subscriber is garbage collected"""
        self._subscribers.discard(ref)

    async def _queue_worker(self) -> None:
        log_entry = await asyncio.wait_for(self.log_queue.get(), timeout=0.1)
        tasks = []
        for ref in list(self._subscribers):
            callback = ref()
            if callback is not None:
                tasks.append(asyncio.create_task(callback(log_entry)))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_queue(self) -> None:
        """Process logs from the queue and notify subscribers"""
        while self._running:
            await self._queue_worker()
            self.log_queue.task_done()


class LogCollector:
    """Captures logs from loguru and forwards them to the central queue"""

    def __init__(
        self, *, backlog: LogBacklog, logger_names: list[str] | None = None
    ) -> None:
        self.backlog = backlog
        self.logger_names = logger_names
        self._sink_id: int | None = None

    def start(self) -> None:
        """Start collecting logs"""
        if self._sink_id is not None:
            return

        self._sink_id = logger.add(sink=self._process_log, level=0)

        logger.info("Log collector started")

    def stop(self) -> None:
        """Stop collecting logs"""
        if self._sink_id is None:
            return
        logger.remove(self._sink_id)
        self._sink_id = None
        logger.info("Log collector stopped")

    def _process_log(self, record) -> Any:
        """Process a log record from loguru"""
        if self.logger_names and record["name"] not in self.logger_names:
            return record["message"]
        try:
            log_entry = LogEntry.create(record)
            asyncio.create_task(self.backlog.enqueue(log_entry))
        except Exception as e:
            logger.error(f"Error processing log: {e}")

        return record["message"]


class RedisPubSub:
    """Handles Redis PubSub operations for distributed logs"""

    def __init__(
        self,
        queue_manager: LogBacklog,
        channel: str,
        *,
        redis: aioredis.Redis,
        batch_size: int = 100,
        flush_interval: float = 0.1,
    ) -> None:
        self.queue_manager = queue_manager
        self.channel = channel
        self.pubsub = None
        self.running = False
        self.redis = redis

        self._listen_task: asyncio.Task | None = None
        self._publish_task: asyncio.Task | None = None

        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.publish_buffer = []
        self.buffer_lock = asyncio.Lock()

    async def connect(self) -> None:
        """Setup Redis PubSub"""
        if self.pubsub:
            return

        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.channel)

    async def disconnect(self) -> None:
        """Clean up Redis PubSub resources"""
        if self.running:
            await self.stop()

        if self.pubsub:
            await self.pubsub.unsubscribe(self.channel)
            await self.pubsub.close()
            self.pubsub = None

    async def start(self) -> None:
        """Start Redis PubSub operations"""
        if self.running:
            return

        if not self.pubsub:
            await self.connect()

        self.running = True

        self._listen_task = asyncio.create_task(self._listen_loop())

        self._publish_task = asyncio.create_task(self._flush_buffer_loop())

        logger.info(f"Redis PubSub started on channel {self.channel}")

    async def stop(self) -> None:
        """Stop Redis PubSub operations"""
        if not self.running:
            return

        self.running = False

        for task in [self._listen_task, self._publish_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._listen_task = None
        self._publish_task = None

        await self._flush_buffer()

        logger.info("Redis PubSub stopped")

    async def publish(self, log_entry: LogEntry) -> None:
        """Buffer a log entry for publication to Redis"""
        if not self.running:
            return

        async with self.buffer_lock:
            self.publish_buffer.append(log_entry)

            if len(self.publish_buffer) >= self.batch_size:
                await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Flush the publish buffer to Redis using pipeline"""
        async with self.buffer_lock:
            if not self.publish_buffer:
                return

            try:
                async with self.redis.pipeline() as pipe:
                    for log_entry in self.publish_buffer:
                        json_data = log_entry.json()
                        pipe.publish(self.channel, json_data)

                    await pipe.execute()

                self.publish_buffer.clear()

            except Exception as e:
                logger.error(f"Error publishing to Redis: {e}")

    async def _flush_buffer_loop(self) -> None:
        try:
            while self.running:
                await asyncio.sleep(self.flush_interval)
                await self._flush_buffer()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception(f"Error in flush buffer loop: {e}")
            if self.running:
                self._publish_task = asyncio.create_task(self._flush_buffer_loop())

    async def _listen_loop(self) -> None:
        """Listen for messages on the Redis channel"""
        try:
            while self.running:
                message = await self.pubsub.get_message(  # type: ignore[union-attr]
                    ignore_subscribe_messages=True, timeout=0.1
                )

                if message is None or message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                    log_entry = LogEntry.model_validate(data)
                    await self.queue_manager.enqueue(log_entry)
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")

                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception(f"Error in Redis listener: {e}")
            if self.running:
                self._listen_task = asyncio.create_task(self._listen_loop())
