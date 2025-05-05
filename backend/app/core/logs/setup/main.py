import logging
from logging.handlers import RotatingFileHandler

import os
import sys
from typing import Callable, Literal

from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from .const import (
    RICH_THEME,
    STDOUT_LOG_FORMAT,
    FILE_LOG_FORMAT
)


def get_formatter(
    target: Literal['console', 'file']
) -> logging.Formatter:
    '''gets the formatter for the logger depending on whether
    it is for stdout or file.

    Args:
        target (Literal['console', 'file']): _the type of formatter to get_

    Returns:
        logging.Formatter: _the formatter_
    '''
    if target == 'console':
        return logging.Formatter(STDOUT_LOG_FORMAT)
    return logging.Formatter(FILE_LOG_FORMAT)


def get_rich_handler() -> RichHandler:
    '''creates a rich handler for the logger.

    Returns:
        RichHandler: _the rich handler_
    '''
    return RichHandler(
        console=Console(
            theme=Theme(RICH_THEME)
        ),
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_time=False,
        show_level=True,
        enable_link_path=True
    )


def create_stdout_handler(
    *,
    use_rich: bool = False,
    level: str = 'DEBUG'
) -> logging.StreamHandler | RichHandler:
    '''gets the appropriate stdout handler for the logger and adds it.

    Args:
        use_rich (bool): _whether to use rich console
            reccomended for development however will slow
            performance in prod_
        level (str): _the log level to set the logger to_
    Returns:
        logging.StreamHandler | RichHandler: _the handler_
    '''
    if use_rich:
        handler = get_rich_handler()
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_formatter('console'))
    handler.setLevel(level)
    return handler


def log_file_path(
    log_dir: str,
    *,
    file_name: str,
    subdir: str | None = None
) -> str:
    '''creates the log file path for the logger.
    Args:
        log_dir (str): _the log directory_
        file_name (str): _the file name_
        subdir (str | None, optional): _the subdirectory_. Defaults to None.
    Returns:
        str: _the log file path_
    '''
    if subdir:
        log_dir = os.path.join(log_dir, subdir)
    return os.path.join(log_dir, file_name)


def create_file_handler(
    *,
    file_path: str,
    level: str,
    max_bytes: int
) -> RotatingFileHandler:
    '''creates a file handler for the logger with the
    with the appropriate file name and level.
    Args:
        file_path (str): the file path for the logger
        level (str): the log level for the logger
        max_bytes (int): the max bytes for the file handler
        before it rolls over
    '''
    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=max_bytes,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(get_formatter('file'))
    
    return file_handler


def configure_uvicorn_logger(
    *,
    level: str = 'INFO',
    uvicorn_audit: bool = False,
    file_path: str = 'uvicorn_access.log',
    max_bytes: int = 10 * 1024 * 1024,
) -> logging.Logger:
    '''Configures the uvicorn access logger for the application.
    in production, enable file logging for auditing purposes.

    Arguments:
        level {str} -- the log level for the logger
        uvicorn_audit {bool} -- whether to enable file logging for 
        auditing purposes

        max_bytes {int} -- the max bytes for the file handler
    '''
    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.setLevel(level)
    if uvicorn_audit:
        file_handler = create_file_handler(
            file_path=file_path,
            level=level,
            max_bytes=max_bytes
        )
        uvicorn_logger.addHandler(file_handler)

    uvicorn_logger.propagate = False
    return uvicorn_logger
