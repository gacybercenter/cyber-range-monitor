from __future__ import annotations

import atexit
import logging
import sys
from typing import TYPE_CHECKING, Any

from loguru import logger as loguru_logger

from server.context import correlation_id

if TYPE_CHECKING:
    from loguru import Logger, Record

    from server.configs.toml import LoggerConfig


class _InterceptHandler(logging.Handler):
    '''
    Ensures all stdlib logs go through loguru allowing
    for the use of the standard logging library in
    3rd party libraries while still having all logs

    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    '''

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _stderr_filter(record: Record) -> bool:
    return record['level'].no >= logging.ERROR


def _stdout_filter(record: Record) -> bool:
    return record['level'].no < logging.ERROR


def add_record_context(record: Record) -> None:
    '''
    A loguru patcher to ensure all logs have a correlation ID.
    '''
    cor_id = correlation_id.get()
    if 'correlation_id' not in record['extra']:
        record['extra']['correlation_id'] = cor_id or 'N/A'


def configure_logging(config: LoggerConfig) -> None:
    '''
    Configures the application logger based on the provided configuration.

    Parameters
    ----------
    config : LoggerConfig
        The logger configuration settings.
    '''
    loguru_logger.remove()
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    dont_propogate = (
        'uvicorn.access',
        'watchfiles.main',
    )

    for handle in logging.root.manager.loggerDict.keys():
        is_noisey = any(handle in loud for loud in dont_propogate)
        logging.getLogger(handle).propagate = not is_noisey

    options = {
        'format': config.format,
        'enqueue': config.enqueue,
        'backtrace': config.backtrace,
        'diagnose': config.diagnose,
        'colorize': config.colorize,
        'serialize': config.structured_stdout,
    }

    handlers: list[Any] = [
        {
            'sink': sys.stdout,
            'level': config.level,
            'filter': _stdout_filter,
            **options,
        },
        {
            'sink': sys.stderr,
            'level': logging.ERROR,
            'filter': _stderr_filter,
            **options,
        },
    ]

    loguru_logger.configure(
        patcher=add_record_context,
        handlers=handlers,
    )

    atexit.register(loguru_logger.complete)


def get_loguru_logger(module: str, **kwargs) -> Logger:
    '''
    Gets the configured loguru logger instance.

    Returns
    -------
    loguru_logger
        The loguru logger instance.
    '''
    return loguru_logger.bind(module=module, **kwargs)
