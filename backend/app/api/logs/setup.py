

import logging
from typing import Any, Self
from app.redis import redis_client


import queue
from .websocket_handler import NonBlockingQueue
from .ws_service import LogSocketManager


def setup_loggers(
    logger_names: list[str],
    q: queue.Queue
) -> None:
    handler = NonBlockingQueue(q=q)
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(handler)


class RealTimeLogger:
    _instance: Self = None  # type: ignore[assignment]
    _queue: queue.Queue = None  # type: ignore[assignment]

    @classmethod
    def initialize(
        cls,
        *,
        logger_names: list[str],
        max_len: int = 1000,
        max_connections: int = 5
    ) -> None:
        if cls._instance:
            raise RuntimeError("RealTimeLogger is already initialized")

        cls._instance = cls()
        cls._queue = queue.Queue(
            maxsize=max_len
        )
        cls._max_connections = max_connections
        setup_loggers(
            logger_names=logger_names,
            q=cls._queue
        )

    @classmethod
    def dependency_maker(cls) -> Any:
        if not cls._instance:
            raise RuntimeError("RealTimeLogger is not initialized and cannot be used.")

        async def get_service() -> LogSocketManager:
            return LogSocketManager(
                q=cls._queue,
                max_connections=cls._max_connections,
                redis=redis_client,
            )

        return get_service
