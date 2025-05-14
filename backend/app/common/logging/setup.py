import logging
import inspect
import os
import sys

from typing import Any, Callable

from loguru import logger
from rich.traceback import install as rich_traceback_install

from .config import log_settings
from .const import (
    LOG_DIR_NAME,
    BASE_LOG_FMT,
    COLOR_LOG_FMT,
    APP_LOG_FILE,
    UVICORN_LOG_FILE
)
    


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        '''Intercepts the log record and sends it to the 
        loguru logger instead of the standard library

        Args:
            record (logging.LogRecord): _the log record_
        '''
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage()
        )


def min_level_filter(level_num: int) -> Callable[[Any], bool]:
    def filter_fn(record: Any) -> bool:
        '''filters the log record based on the level.

        Args:
            record (dict[str, str]): _the log record_

        Returns:
            bool: _True if the level is greater than or equal to the minimum level._
        '''
        return record['level'].no >= level_num

    return filter_fn


def add_console_handler(
    *,
    dev_mode: bool = True,
    level: str = 'DEBUG',
    std_level_filter: int | None = None,
) -> int:
    '''adds a console handler to the logger.

    Args:
        dev_mode (bool, optional): _whether it's development mode_. Defaults to True.
        level (str, optional): _description_. Defaults to 'DEBUG'.
        std_level_filter (int | None, optional): _description_. Defaults to None.

    Returns:
        int: _loguru ID_
    '''

    log_format = COLOR_LOG_FMT if dev_mode else BASE_LOG_FMT
    level_filter = None
    if std_level_filter:
        level_filter = min_level_filter(std_level_filter)

    return logger.add(
        sink=sys.stdout,
        format=log_format,
        colorize=dev_mode,
        backtrace=True,
        level=level,
        diagnose=dev_mode,
        filter=level_filter,
        enqueue=True
    )


def add_file_handler(
    *,
    level: str = 'DEBUG',
    max_bytes_mb: int = 5,
    file_level_filter: int | None = None,
) -> int:
    '''adds a file handler to the logger.

    Args:
        level (str, optional): the level for the file handler. Defaults to 'DEBUG'.
        max_bytes_mb (int, optional): __. Defaults to 5.
        file_name (str, optional): _description_. Defaults to 'app.log'.

    Returns:
        int: _loguru ID_
    '''

    def file_filter(record: Any) -> bool:
        '''filters the log record based on the level.

        Args:
            record (dict[str, str]): _the log record_

        Returns:
            bool: _True if the level is greater than or equal to the minimum level._
        '''
        return record['name'] == 'error' or record['name'] == 'access'

    level_filter = file_filter
    if file_level_filter:
        log_lvl_filter = min_level_filter(file_level_filter)
        level_filter = lambda record: log_lvl_filter(record) and file_filter(record)

    return logger.add(
        sink=os.path.join(
            LOG_DIR_NAME, 
            APP_LOG_FILE
        ),
        format=BASE_LOG_FMT,
        rotation=(max_bytes_mb * 1024 * 1024),
        compression='zip',
        level=level,
        filter=level_filter,
        enqueue=True
    )


def intercept_std_logger(
    std_logger: logging.Logger,
    *,
    propagate: bool = False
) -> logging.Logger:
    if std_logger.hasHandlers():
        std_logger.handlers.clear()
    std_logger.addHandler(InterceptHandler())
    std_logger.propagate = propagate
    return std_logger


def setup_uvicorn_logger(
    *,
    level_name: str = 'INFO',
    uvicorn_audit: bool = True,
    max_bytes_mb: int = 5,
) -> None:
    '''Sets up the uvicorn logger to use the loguru logger.

    Args:
        level_name (str, optional): _the level for the uvicorn logger_. Defaults to 'INFO'.
    '''
    uvicorn_logger = intercept_std_logger(
        logging.getLogger('uvicorn'),
        propagate=False
    )
    uvicorn_logger.propagate = False
    uvicorn_logger.setLevel(level_name)

    def is_uvicorn_logger(record: Any) -> bool:
        return record['name'].startswith('uvicorn.')

    if uvicorn_audit:
        logger.add(
            sink=os.path.join(
                LOG_DIR_NAME, UVICORN_LOG_FILE
            ),
            format=BASE_LOG_FMT,
            rotation=(max_bytes_mb * 1024 * 1024),
            compression='zip',
            level=level_name,
            filter=is_uvicorn_logger,
            enqueue=True
        )


def app_logger_setup(dev_mode: bool) -> None:
    os.makedirs(LOG_DIR_NAME, exist_ok=True)
    if dev_mode:
        rich_traceback_install(
            show_locals=True
        )

    logging.root.setLevel(logging.NOTSET)
    intercept_std_logger(logging.root)
    intercept_std_logger(
        logging.getLogger('app'),
        propagate=False
    )


def init_app_loggers(dev_mode: bool = True) -> None:
    '''initializes logging for the application.

    Args:
        dev_mode (bool, optional): _description_. Defaults to True.

    Returns:
        Logger: _the loguru logger_
    '''

    app_logger_setup(dev_mode=dev_mode)

    level_names = log_settings.level_name
    level_filters = log_settings.level_filters

    logger.remove()

    add_console_handler(
        dev_mode=dev_mode,
        level=level_names.std_level,
        std_level_filter=level_filters.std_level
    )

    add_file_handler(
        level=level_names.file_level,
        max_bytes_mb=log_settings.rotation_megabytes,
        file_level_filter=level_filters.file_level
    )

    if log_settings.uvicorn_audit:
        setup_uvicorn_logger(
            level_name=level_names.uvicorn_level,
            uvicorn_audit=log_settings.uvicorn_audit,
            max_bytes_mb=log_settings.rotation_megabytes
        )
    

