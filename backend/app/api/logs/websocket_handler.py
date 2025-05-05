

import asyncio
import json

from datetime import datetime
import logging
from typing import Any, Dict, List
from .schema import LogEntry


class AsyncQueueHandler(logging.Handler):

    def __init__(self, queue: asyncio.Queue) -> None:
        super().__init__()
        self.queue: asyncio.Queue = queue

    def emit(self, record: logging.LogRecord) -> None:
        try:
            as_entry = LogEntry.create(
                record=record
            )
            try:
                self.queue.put_nowait(as_entry)
            except asyncio.QueueFull:
                pass
        except Exception as e:
            self.handleError(record)


def setup_async_queue_handler(
    queue: asyncio.Queue,
    logger_names: List[str]
) -> None:
    """Sets up the async queue handler for logging."""
    handler = AsyncQueueHandler(queue)

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.propagate = False


def remove_async_queue_handler(
    logger_names: List[str]
) -> None:
    """Removes the async queue handler from the specified loggers."""
    def is_queue_handler(handler: logging.Handler) -> bool:
        return isinstance(handler, AsyncQueueHandler)

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        for handler in list(filter(is_queue_handler, logger.handlers)):
            logger.removeHandler(handler)

    